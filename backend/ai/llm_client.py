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
