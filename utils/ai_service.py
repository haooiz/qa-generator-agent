"""Azure OpenAI API 연동 서비스."""

import json
import os
import re

from dotenv import load_dotenv
from openai import AzureOpenAI

from utils.prompts import build_evaluation_prompt, build_generation_prompt

load_dotenv()

DEFAULT_AZURE_ENDPOINT = "https://skax.ai-talentlab.com"
DEFAULT_AZURE_API_VERSION = "2024-12-01-preview"
DEFAULT_MODEL = "gpt-4.1"


def _get_secret(key: str, default: str = "") -> str:
    """로컬 .env 또는 Streamlit Cloud Secrets에서 값을 읽습니다."""
    value = os.getenv(key, default)
    if value and value not in ("your_openai_api_key_here", "your_azure_openai_api_key_here"):
        return value

    try:
        import streamlit as st

        if key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass

    return default


def _get_client() -> AzureOpenAI:
    api_key = _get_secret("OPENAI_API_KEY") or _get_secret("AZURE_OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY(또는 AZURE_OPENAI_API_KEY)가 설정되지 않았습니다. "
            "로컬: .env 파일 / Streamlit Cloud: Settings → Secrets에 키를 입력해 주세요."
        )
    return AzureOpenAI(
        azure_endpoint=_get_secret("AZURE_OPENAI_ENDPOINT", DEFAULT_AZURE_ENDPOINT),
        api_key=api_key,
        api_version=_get_secret("AZURE_OPENAI_API_VERSION", DEFAULT_AZURE_API_VERSION),
    )


def _get_model() -> str:
    return _get_secret("OPENAI_MODEL", DEFAULT_MODEL)


def _parse_json_response(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned)


def generate_qa_content(
    document_text: str,
    learning_purpose: str,
    question_types: list[str],
    difficulty: str,
    num_questions: int,
) -> dict:
    client = _get_client()
    prompt = build_generation_prompt(
        document_text, learning_purpose, question_types, difficulty, num_questions
    )

    response = client.chat.completions.create(
        model=_get_model(),
        messages=[
            {
                "role": "system",
                "content": "당신은 교육 콘텐츠 생성 전문가입니다. 항상 유효한 JSON만 반환하세요.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content or "{}"
    return _parse_json_response(content)


def evaluate_user_answer(
    question: dict,
    user_answer: str,
    document_context: str,
) -> dict:
    client = _get_client()
    prompt = build_evaluation_prompt(question, user_answer, document_context)

    response = client.chat.completions.create(
        model=_get_model(),
        messages=[
            {
                "role": "system",
                "content": "당신은 친절한 학습 코치입니다. 항상 유효한 JSON만 반환하세요.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content or "{}"
    return _parse_json_response(content)
