import re
import uuid
from typing import Any
from backend.ai.tools import TOOL_REGISTRY
from backend.schemas import ChatProposal, ChatRequest, ChatResponse, ToolUsed
from backend.services.audit_service import log_event


INV_ID_REGEX = re.compile(r"\b([A-Z]{2,5}-\d{2,})\b", re.IGNORECASE)


def process_chat_message(chat_req: ChatRequest) -> ChatResponse:
    message = chat_req.message.strip()
    session_id = chat_req.session_id or f"sess-{uuid.uuid4().hex[:12]}"
    upload_id = chat_req.upload_id

    tools_used: list[ToolUsed] = []
    collected_cards: list[dict[str, Any]] = []
    proposal_obj: ChatProposal | None = None
    reply = ""

    msg_lower = message.lower()
    inv_matches = INV_ID_REGEX.findall(message)
    target_inv_id = inv_matches[0].upper() if inv_matches else None

    # Intent routing
    if any(k in msg_lower for k in ("why", "explain", "reason")) and target_inv_id:
        res = TOOL_REGISTRY["explain_decision"](target_inv_id)
        tools_used.append(ToolUsed(name="explain_decision", arguments={"invoice_id": target_inv_id}))
        if "error" in res:
            reply = f"I could not find invoice {target_inv_id} in the database."
        else:
            data = res["data"]
            collected_cards.extend(res.get("cards", []))
            matched = data.get("matched_record")
            if matched:
                reply = f"Invoice {target_inv_id} was flagged with decision '{data['decision']}' because: {data['primary_reason']}. It matched record {matched}."
            else:
                reply = f"Invoice {target_inv_id} was flagged with decision '{data['decision']}' because: {data['primary_reason']}."

    elif any(k in msg_lower for k in ("approve", "reject")) and target_inv_id:
        action = "approve" if "approve" in msg_lower else "reject"
        res = TOOL_REGISTRY["propose_review"](target_inv_id, action)
        tools_used.append(ToolUsed(name="propose_review", arguments={"invoice_id": target_inv_id, "action": action}))
        if "error" in res:
            reply = res.get("message", f"Could not propose review for {target_inv_id}.")
        else:
            prop = res.get("proposal")
            if prop:
                proposal_obj = ChatProposal(**prop)
                reply = f"I suggest {action}ing invoice {target_inv_id}. Please confirm with the button below."
            else:
                reply = f"Unable to propose review for {target_inv_id}."

    elif any(k in msg_lower for k in ("duplicate", "duplicates")):
        res = TOOL_REGISTRY["list_duplicates"](10)
        tools_used.append(ToolUsed(name="list_duplicates", arguments={"limit": 10}))
        collected_cards.extend(res.get("cards", []))
        count = len(res.get("data", []))
        reply = f"I found {count} duplicate invoices requiring review."

    elif any(k in msg_lower for k in ("riskiest", "pending", "queue", "risky", "need review")):
        res = TOOL_REGISTRY["list_pending"](5)
        tools_used.append(ToolUsed(name="list_pending", arguments={"limit": 5}))
        collected_cards.extend(res.get("cards", []))
        count = len(res.get("data", []))
        reply = f"Here are {count} pending invoices needing attention, sorted lowest confidence first."

    elif any(k in msg_lower for k in ("how many", "stats", "summary", "rate", "metrics")):
        res = TOOL_REGISTRY["get_stats"](upload_id)
        tools_used.append(ToolUsed(name="get_stats", arguments={"upload_id": upload_id}))
        collected_cards.extend(res.get("cards", []))
        s = res["data"]
        reply = f"Overall summary: {s['total']} invoices processed. {s['by_decision']['auto_pass']} auto-passed ({s['auto_pass_rate']:.1%}), {s['by_decision']['needs_review']} need review, and {s['by_decision']['exception']} are exceptions."

    elif any(k in msg_lower for k in ("report", "download", "export", "csv")):
        res = TOOL_REGISTRY["get_report_link"](upload_id)
        tools_used.append(ToolUsed(name="get_report_link", arguments={"upload_id": upload_id}))
        collected_cards.extend(res.get("cards", []))
        reply = "You can download the exceptions short report CSV using the link below."

    elif any(k in msg_lower for k in ("audit", "history", "timeline")) and target_inv_id:
        res = TOOL_REGISTRY["get_audit"](target_inv_id, 10)
        tools_used.append(ToolUsed(name="get_audit", arguments={"invoice_id": target_inv_id, "limit": 10}))
        count = len(res.get("data", []))
        reply = f"Found {count} audit log events recorded for invoice {target_inv_id}."

    elif any(k in msg_lower for k in ("exception", "exceptions", "flag", "flagged")):
        res = TOOL_REGISTRY["list_exceptions"](None, 10)
        tools_used.append(ToolUsed(name="list_exceptions", arguments={"limit": 10}))
        collected_cards.extend(res.get("cards", []))
        count = len(res.get("data", []))
        reply = f"Found {count} flagged invoices with exceptions."

    elif target_inv_id:
        res = TOOL_REGISTRY["get_invoice"](target_inv_id)
        tools_used.append(ToolUsed(name="get_invoice", arguments={"invoice_id": target_inv_id}))
        if "error" in res:
            reply = f"I could not find invoice {target_inv_id}."
        else:
            collected_cards.extend(res.get("cards", []))
            reply = f"Here is invoice {target_inv_id}."

    else:
        reply = "I am your Accounts Payable Assistant. You can ask me:\n- 'Why was INV-1042 flagged?'\n- 'Show the riskiest invoices'\n- 'Show all duplicates'\n- 'Download the report'\n- 'What are the current stats?'"

    # De-duplicate cards by invoice id and cap at 5
    seen_ids = set()
    final_cards = []
    for c in collected_cards:
        cid = c.get("invoice_id") or c.get("id") or c.get("url")
        if cid not in seen_ids:
            seen_ids.add(cid)
            final_cards.append(c)
        if len(final_cards) >= 5:
            break

    # Collect referenced invoice IDs
    ref_ids = set()
    for m in INV_ID_REGEX.findall(reply):
        ref_ids.add(m.upper())
    for c in final_cards:
        if c.get("invoice_id"):
            ref_ids.add(c["invoice_id"])
        if c.get("matched_record"):
            ref_ids.add(c["matched_record"])

    # Audit log
    log_event(
        actor="ai-assistant",
        actor_type="ai",
        event_type="CHAT_QUERY",
        details={
            "message": message,
            "session_id": session_id,
            "tools_used": [t.model_dump() for t in tools_used],
        },
    )

    return ChatResponse(
        reply=reply,
        session_id=session_id,
        referenced_invoice_ids=sorted(list(ref_ids)),
        tools_used=tools_used,
        cards=final_cards,
        proposal=proposal_obj,
    )
