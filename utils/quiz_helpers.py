"""퀴즈 채점 헬퍼."""

import re


def check_objective_answer(question: dict, user_answer: str) -> bool:
    """객관식·OX 정답 여부를 판별합니다."""
    correct = (question.get("answer") or "").strip()
    user = user_answer.strip()

    if not user or user == "선택하세요":
        return False
    if user == correct:
        return True

    correct_lower = correct.lower()
    user_lower = user.lower()
    if correct_lower == user_lower:
        return True

    correct_prefix = re.match(r"^[①②③④⑤⑥]|\d+", correct)
    user_prefix = re.match(r"^[①②③④⑤⑥]|\d+", user)
    if correct_prefix and user_prefix and correct_prefix.group() == user_prefix.group():
        return True

    if correct in user or user in correct:
        return True

    return False
