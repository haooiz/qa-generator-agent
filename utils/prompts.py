"""AI 프롬프트 템플릿."""

LEARNING_PURPOSE_LABELS = {
    "exam": "시험 대비",
    "interview": "면접 대비",
    "work": "업무 지식 습득",
    "certification": "자격증 공부",
}

DIFFICULTY_LABELS = {
    "beginner": "초급",
    "intermediate": "중급",
    "advanced": "고급",
}

QUESTION_TYPE_LABELS = {
    "multiple_choice": "객관식",
    "subjective": "주관식",
    "ox": "OX 문제",
    "interview": "면접 질문",
    "descriptive": "서술형",
}


def build_generation_prompt(
    document_text: str,
    learning_purpose: str,
    question_types: list[str],
    difficulty: str,
    num_questions: int,
) -> str:
    type_list = ", ".join(QUESTION_TYPE_LABELS[t] for t in question_types)
    purpose = LEARNING_PURPOSE_LABELS.get(learning_purpose, learning_purpose)
    level = DIFFICULTY_LABELS.get(difficulty, difficulty)

    return f"""당신은 교육 전문 AI입니다. 아래 문서를 분석하여 학습 자료와 문제를 생성하세요.

## 학습 목적
{purpose}

## 생성 조건
- 문제 유형: {type_list}
- 난이도: {level}
- 총 문제 수: {num_questions}개 (선택된 유형에 고르게 분배)

## 문서 내용
{document_text[:12000]}

## 출력 형식 (반드시 JSON만 반환, 마크다운 코드블록 없이)
{{
  "summary": ["핵심 요약 항목1", "핵심 요약 항목2", ...],
  "questions": [
    {{
      "id": 1,
      "type": "multiple_choice",
      "question": "문제 내용",
      "options": ["① 선택지1", "② 선택지2", "③ 선택지3", "④ 선택지4"],
      "answer": "정답 (번호 또는 선택지 텍스트)",
      "explanation": "해설 (선택)"
    }},
    {{
      "id": 2,
      "type": "subjective",
      "question": "문제 내용",
      "answer": "정답 예시",
      "explanation": "채점 포인트"
    }},
    {{
      "id": 3,
      "type": "ox",
      "question": "O/X 문제 내용",
      "answer": "O 또는 X",
      "explanation": "해설"
    }},
    {{
      "id": 4,
      "type": "interview",
      "question": "면접 질문",
      "answer": "모범 답변 예시",
      "explanation": "면접관이 보는 포인트"
    }},
    {{
      "id": 5,
      "type": "descriptive",
      "question": "서술형 문제",
      "answer": "모범 답안",
      "explanation": "채점 기준"
    }}
  ],
  "learning_analysis": {{
    "recommended_topics": ["복습 영역1", "복습 영역2", "복습 영역3"],
    "analysis_comment": "문서 난이도 및 학습자 관점의 한 줄 코멘트 (점수 없이)"
  }}
}}

type 필드는 반드시 다음 중 하나: multiple_choice, subjective, ox, interview, descriptive
comprehension_score나 점수는 생성하지 마세요. 점수는 사용자가 답변한 후에만 산출됩니다.
"""


def build_evaluation_prompt(
    question: dict,
    user_answer: str,
    document_context: str,
) -> str:
    q_type = QUESTION_TYPE_LABELS.get(question.get("type", ""), question.get("type", ""))
    return f"""당신은 학습 코치 AI입니다. 사용자의 답변을 평가하세요.

## 참고 문서 (일부)
{document_context[:4000]}

## 문제
유형: {q_type}
질문: {question.get("question", "")}
모범 답안: {question.get("answer", "")}

## 사용자 답변
{user_answer}

## 출력 형식 (반드시 JSON만 반환)
{{
  "score": 85,
  "strengths": ["강점1", "강점2"],
  "improvements": ["보완점1", "보완점2"],
  "feedback": "종합 피드백 한 문단"
}}
score는 0~100 정수
"""
