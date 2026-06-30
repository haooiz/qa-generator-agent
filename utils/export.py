"""질문·정답 엑셀보내기."""

from io import BytesIO

from utils.export_template import (
    CONTENT_COL_END,
    DATA_START_ROW,
    HEADER_ROW,
    apply_data_row_style,
    load_export_template,
)
from utils.prompts import QUESTION_TYPE_LABELS


def _format_options(options: list[str] | None) -> str:
    if not options:
        return ""
    return "\n".join(options)


def _format_result(submission: dict) -> str:
    if not submission.get("checked"):
        return ""
    if "is_correct" in submission:
        return "정답" if submission["is_correct"] else "오답"
    score = submission.get("score")
    return f"{score}점" if score is not None else ""


def _fill_meta_rows(ws, document_name: str, summary_text: str, topics_text: str) -> None:
    """1~3행 B~I 병합 영역에 데이터만 입력 (서식은 템플릿 유지)."""
    values = (document_name, summary_text, topics_text)
    for row, value in enumerate(values, 1):
        ws.cell(row=row, column=2, value=value)


def build_qa_excel(
    result: dict,
    quiz_submissions: dict | None = None,
    document_name: str = "",
) -> bytes:
    """템플릿 서식을 유지한 채 질문·정답 데이터를 채웁니다."""
    quiz_submissions = quiz_submissions or {}
    questions = result.get("questions", [])
    summary = result.get("summary", [])
    analysis = result.get("learning_analysis", {})

    wb = load_export_template()
    ws = wb.active

    if ws.max_row >= DATA_START_ROW:
        ws.delete_rows(DATA_START_ROW, ws.max_row - DATA_START_ROW + 1)

    summary_text = "\n".join(f"• {item}" for item in summary) if summary else ""
    topics_text = ", ".join(analysis.get("recommended_topics", []))
    _fill_meta_rows(ws, document_name, summary_text, topics_text)

    row = DATA_START_ROW
    for i, q in enumerate(questions):
        q_id = q.get("id", i + 1)
        q_key = str(q_id)
        submission = quiz_submissions.get(q_key, {})
        q_type = q.get("type", "")
        type_label = QUESTION_TYPE_LABELS.get(q_type, q_type)

        values = [
            q_id,
            type_label,
            q.get("question", ""),
            _format_options(q.get("options")),
            q.get("answer", ""),
            q.get("explanation", ""),
            submission.get("user_answer", ""),
            _format_result(submission),
            submission.get("score", ""),
        ]
        for col, value in enumerate(values, 1):
            ws.cell(row=row, column=col, value=value)
        apply_data_row_style(ws, row)
        row += 1

    ws.freeze_panes = f"A{DATA_START_ROW}"

    buffer = BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def make_export_filename(document_name: str = "") -> str:
    base = "질의응답"
    if document_name:
        stem = document_name.rsplit(".", 1)[0]
        base = f"{stem}_질의응답"
    return f"{base}.xlsx"
