import json
from typing import Any
from backend.ai.prompts import SYSTEM_SUMMARY
from backend.settings import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_DEPLOYMENT,
    AZURE_OPENAI_ENDPOINT,
)


def call_azure_summary(decision_record: dict[str, Any]) -> dict[str, Any]:
    from openai import AzureOpenAI

    client = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
    )

    response = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=[
            {"role": "system", "content": SYSTEM_SUMMARY},
            {"role": "user", "content": json.dumps(decision_record)},
        ],
        response_format={"type": "json_object"},
        temperature=0.0,
        max_tokens=300,
    )

    content = response.choices[0].message.content or "{}"
    return json.loads(content)


def call_gemini_summary(decision_record: dict[str, Any]) -> dict[str, Any]:
    import httpx
    from backend.settings import GEMINI_API_KEY, GEMINI_MODEL

    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    prompt_text = f"{SYSTEM_SUMMARY}\n\nInvoice Record JSON:\n{json.dumps(decision_record)}"

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt_text}]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.0,
        },
    }

    with httpx.Client(timeout=15.0) as client:
        res = client.post(url, json=payload)
        res.raise_for_status()
        data = res.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(raw_text)
