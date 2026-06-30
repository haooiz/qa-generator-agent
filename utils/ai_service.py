"""OpenAI API 연동 서비스."""

import json
import os
import re

from dotenv import load_dotenv
from openai import OpenAI

from utils.prompts import build_evaluation_prompt, build_generation_prompt

load_dotenv()


def _get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        raise ValueError(
            "OPENAI_API_KEY가 설정되지 않았습니다. "
            ".env 파일에 API 키를 입력하거나 환경 변수를 설정해 주세요."
        )
    return OpenAI(api_key=api_key)


def _get_model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")


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
