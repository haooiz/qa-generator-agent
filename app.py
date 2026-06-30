"""질의응답 생성 Streamlit 앱."""

import streamlit as st

from utils.ai_service import evaluate_user_answer, generate_qa_content
from utils.document_parser import SUPPORTED_EXTENSIONS, parse_document
from utils.prompts import DIFFICULTY_LABELS, LEARNING_PURPOSE_LABELS, QUESTION_TYPE_LABELS
from utils.export import build_qa_excel, make_export_filename
from utils.quiz_helpers import check_objective_answer

OBJECTIVE_TYPES = {"multiple_choice", "ox"}

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="AI 질의응답 생성기",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 커스텀 스타일 ────────────────────────────────────────────
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #1E3A5F;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #5A6A7E;
        margin-bottom: 1.5rem;
    }
    .section-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
    }
    .score-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        margin: 1rem 0;
    }
    .score-number {
        font-size: 3rem;
        font-weight: 800;
        line-height: 1;
    }
    .score-label {
        font-size: 0.9rem;
        opacity: 0.9;
        margin-top: 0.3rem;
    }
    .growth-badge {
        display: inline-block;
        background: #10B981;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .question-card {
        background: white;
        border-left: 4px solid #667eea;
        padding: 1rem 1.2rem;
        margin: 0.8rem 0;
        border-radius: 0 8px 8px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .answer-box {
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        margin-top: 0.5rem;
    }
    .wrong-box {
        background: #FEF2F2;
        border: 1px solid #FECACA;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        margin-top: 0.5rem;
    }
  </style>
    """,
    unsafe_allow_html=True,
)

# ── 세션 상태 초기화 ─────────────────────────────────────────
DEFAULTS = {
    "document_text": "",
    "uploaded_filename": "",
    "generation_result": None,
    "quiz_submissions": {},
}
for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── 헤더 ──────────────────────────────────────────────────────
st.markdown('<p class="main-header">📚 AI 질의응답 생성기</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">문서를 업로드하고 AI가 맞춤형 학습 문제와 성장 분석을 제공합니다.</p>',
    unsafe_allow_html=True,
)

col_left, col_right = st.columns([1, 1], gap="large")

# ══════════════════════════════════════════════════════════════
# ① 문서 업로드
# ══════════════════════════════════════════════════════════════
with col_left:
    st.markdown("### ① 문서 업로드")

    uploaded_file = st.file_uploader(
        "학습 문서를 업로드하세요",
        type=["pdf", "docx", "pptx", "txt"],
        help="PDF, DOCX, PPTX, TXT 파일을 지원합니다. (구형 .ppt는 PPTX로 저장 후 업로드)",
    )

    if uploaded_file:
        try:
            file_bytes = uploaded_file.read()
            text = parse_document(uploaded_file.name, file_bytes)
            st.session_state.document_text = text
            st.session_state.uploaded_filename = uploaded_file.name
            st.success(f"✅ **{uploaded_file.name}** 업로드 완료 ({len(text):,}자 추출)")
            with st.expander("추출된 텍스트 미리보기", expanded=False):
                st.text(text[:2000] + ("..." if len(text) > 2000 else ""))
        except Exception as e:
            st.error(f"문서 파싱 오류: {e}")

    st.markdown("---")
    st.markdown("**📚 학습 목적**")
    learning_purpose = st.radio(
        "학습 목적을 선택하세요",
        options=list(LEARNING_PURPOSE_LABELS.keys()),
        format_func=lambda x: LEARNING_PURPOSE_LABELS[x],
        label_visibility="collapsed",
    )

# ══════════════════════════════════════════════════════════════
# ② 문제 생성 옵션
# ══════════════════════════════════════════════════════════════
with col_right:
    st.markdown("### ② 문제 생성 옵션")

    st.markdown("**문제 유형**")
    selected_types = []
    type_cols = st.columns(2)
    type_keys = list(QUESTION_TYPE_LABELS.keys())
    for i, q_type in enumerate(type_keys):
        with type_cols[i % 2]:
            if st.checkbox(QUESTION_TYPE_LABELS[q_type], value=True, key=f"type_{q_type}"):
                selected_types.append(q_type)

    st.markdown("**난이도**")
    difficulty = st.radio(
        "난이도",
        options=list(DIFFICULTY_LABELS.keys()),
        format_func=lambda x: DIFFICULTY_LABELS[x],
        horizontal=True,
        label_visibility="collapsed",
    )

    st.markdown("**문제 수**")
    count_option = st.radio(
        "문제 수",
        options=["5", "10", "20", "custom"],
        format_func=lambda x: {"5": "5개", "10": "10개", "20": "20개", "custom": "사용자 지정"}[x],
        horizontal=True,
        label_visibility="collapsed",
    )

    if count_option == "custom":
        num_questions = st.number_input("문제 수 입력", min_value=1, max_value=50, value=15)
    else:
        num_questions = int(count_option)

    generate_btn = st.button(
        "🚀 AI 문제 생성",
        type="primary",
        use_container_width=True,
        disabled=not st.session_state.document_text or not selected_types,
    )

st.markdown("---")

# ── 생성 실행 ────────────────────────────────────────────────
if generate_btn:
    if not st.session_state.document_text:
        st.warning("먼저 문서를 업로드해 주세요.")
    elif not selected_types:
        st.warning("최소 하나의 문제 유형을 선택해 주세요.")
    else:
        with st.spinner("AI가 문서를 분석하고 문제를 생성하는 중..."):
            try:
                result = generate_qa_content(
                    document_text=st.session_state.document_text,
                    learning_purpose=learning_purpose,
                    question_types=selected_types,
                    difficulty=difficulty,
                    num_questions=num_questions,
                )
                st.session_state.generation_result = result
                st.session_state.quiz_submissions = {}
                st.success("문제 생성이 완료되었습니다! 아래 문제에 답한 뒤 **정답 확인**을 눌러 주세요.")
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"생성 중 오류가 발생했습니다: {e}")

result = st.session_state.generation_result

# ══════════════════════════════════════════════════════════════
# ③ AI 생성 결과
# ══════════════════════════════════════════════════════════════
if result:
    st.markdown("### ③ AI 생성 결과")

    # 핵심 요약
    summary = result.get("summary", [])
    if summary:
        st.markdown("#### 📋 핵심 요약")
        for item in summary:
            st.markdown(f"- {item}")

    st.markdown("---")

    # 생성 문제 — 정답은 확인 버튼 이후에만 공개
    questions = result.get("questions", [])
    if questions:
        st.markdown("#### 📝 생성 문제")
        st.caption("답을 선택하거나 입력한 뒤 **정답 확인** 버튼을 눌러 주세요.")

        for i, q in enumerate(questions):
            q_type = q.get("type", "")
            type_label = QUESTION_TYPE_LABELS.get(q_type, q_type)
            q_id = q.get("id", i + 1)
            q_key = str(q_id)

            st.markdown(
                f'<div class="question-card">'
                f'<strong>[{type_label}] Q{q_id}.</strong> {q.get("question", "")}'
                f"</div>",
                unsafe_allow_html=True,
            )

            if q_type == "multiple_choice" and q.get("options"):
                user_input = st.radio(
                    "답을 선택하세요",
                    options=["선택하세요", *q["options"]],
                    key=f"ans_{i}",
                    label_visibility="collapsed",
                )
            elif q_type == "ox":
                user_input = st.radio(
                    "O 또는 X를 선택하세요",
                    options=["선택하세요", "O", "X"],
                    key=f"ans_{i}",
                    horizontal=True,
                    label_visibility="collapsed",
                )
            else:
                user_input = st.text_area(
                    "답변을 입력하세요",
                    height=100,
                    placeholder="답변을 작성해 주세요...",
                    key=f"ans_{i}",
                    label_visibility="collapsed",
                )

            if st.button("✅ 정답 확인", key=f"check_{i}", use_container_width=True):
                if not user_input or user_input == "선택하세요":
                    st.warning("답을 선택하거나 입력해 주세요.")
                else:
                    submission = {"user_answer": user_input, "checked": True}
                    try:
                        if q_type in OBJECTIVE_TYPES:
                            is_correct = check_objective_answer(q, user_input)
                            submission["is_correct"] = is_correct
                            submission["score"] = 100 if is_correct else 0
                        else:
                            evaluation = evaluate_user_answer(
                                question=q,
                                user_answer=user_input,
                                document_context=st.session_state.document_text,
                            )
                            submission["score"] = evaluation.get("score", 0)
                            submission["strengths"] = evaluation.get("strengths", [])
                            submission["improvements"] = evaluation.get("improvements", [])
                            submission["feedback"] = evaluation.get("feedback", "")
                        st.session_state.quiz_submissions[q_key] = submission
                    except ValueError as e:
                        st.error(str(e))
                    except Exception as e:
                        st.error(f"채점 중 오류가 발생했습니다: {e}")

            submission = st.session_state.quiz_submissions.get(q_key)
            if submission and submission.get("checked"):
                if q_type in OBJECTIVE_TYPES:
                    if submission.get("is_correct"):
                        st.success("✅ 정답입니다!")
                    else:
                        st.error("❌ 오답입니다.")
                else:
                    st.metric("채점 결과", f"{submission.get('score', 0)}점 / 100점")

                st.markdown(
                    f'<div class="answer-box">📌 <strong>정답:</strong> {q.get("answer", "")}</div>',
                    unsafe_allow_html=True,
                )
                if q.get("explanation"):
                    st.caption(f"💡 {q['explanation']}")

                if q_type not in OBJECTIVE_TYPES:
                    if submission.get("strengths"):
                        st.markdown("**강점**")
                        for s in submission["strengths"]:
                            st.markdown(f"- ✅ {s}")
                    if submission.get("improvements"):
                        st.markdown("**보완점**")
                        for imp in submission["improvements"]:
                            st.markdown(f"- 🔸 {imp}")
                    if submission.get("feedback"):
                        st.info(submission["feedback"])

            st.markdown("---")

    st.markdown("### ④ 성장 지원 기능")
    st.markdown('<span class="growth-badge">🌱 성장 지원 Agent</span>', unsafe_allow_html=True)

    analysis = result.get("learning_analysis", {})
    submissions = [
        s for s in st.session_state.quiz_submissions.values() if s.get("checked")
    ]

    # ── 1. 학습 이해도 (맨 위) ──────────────────────────────
    score_col1, score_col2, score_col3 = st.columns([1, 2, 1])
    with score_col2:
        if submissions:
            avg_score = round(
                sum(s.get("score", 0) for s in submissions) / len(submissions)
            )
            correct_count = sum(1 for s in submissions if s.get("is_correct"))
            objective_count = sum(1 for s in submissions if "is_correct" in s)
            st.markdown(
                f"""
                <div class="score-box">
                    <div class="score-label">학습 이해도</div>
                    <div class="score-number">{avg_score}점</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption(
                f"채점 완료 {len(submissions)}문제 · "
                f"객관식/OX 정답 {correct_count}/{objective_count}"
                if objective_count
                else f"채점 완료 {len(submissions)}문제"
            )
        else:
            st.markdown(
                """
                <div class="score-box">
                    <div class="score-label">학습 이해도</div>
                    <div class="score-number">—</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption("문제에 답변하고 **정답 확인**을 완료하면 점수가 표시됩니다.")

    st.markdown("---")

    # ── 2. 추천 복습 영역 | 취약점 분석 (나란히) ─────────────
    all_strengths: list[str] = []
    all_improvements: list[str] = []
    for s in submissions:
        all_strengths.extend(s.get("strengths", []))
        all_improvements.extend(s.get("improvements", []))

    rec_col, weak_col = st.columns(2, gap="large")

    with rec_col:
        st.markdown("#### 📌 추천 복습 영역")
        topics = analysis.get("recommended_topics", [])
        if topics:
            for topic in topics:
                st.markdown(f"- **{topic}**")
        else:
            st.caption("문서 분석 후 추천 영역이 표시됩니다.")
        if analysis.get("analysis_comment"):
            st.info(analysis["analysis_comment"])

    with weak_col:
        st.markdown("#### 🔍 취약점 분석")
        if all_strengths or all_improvements:
            inner_col1, inner_col2 = st.columns(2)
            with inner_col1:
                st.markdown("**💪 강점**")
                for item in dict.fromkeys(all_strengths):
                    st.markdown(f"- ✅ {item}")
            with inner_col2:
                st.markdown("**📈 보완점**")
                for item in dict.fromkeys(all_improvements):
                    st.markdown(f"- 🔸 {item}")
        else:
            st.info("답변 채점 후 강점·보완점이 표시됩니다.")

    st.markdown("---")

    # ── 3. 엑셀 다운로드 (맨 아래) ───────────────────────────
    if questions:
        st.download_button(
            label="📥 질문·정답 엑셀 다운로드",
            data=build_qa_excel(
                result=result,
                quiz_submissions=st.session_state.quiz_submissions,
                document_name=st.session_state.uploaded_filename,
            ),
            file_name=make_export_filename(st.session_state.uploaded_filename),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
        st.caption(
            "서식(열 너비·병합 등)은 `templates/qa_export_template.xlsx` 를 Excel에서 직접 수정할 수 있습니다."
        )

else:
    st.info("문서를 업로드하고 **AI 문제 생성** 버튼을 눌러 결과를 확인하세요.")

# ── 사이드바 ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ℹ️ 사용 안내")
    st.markdown(
        """
        1. **문서 업로드** — PDF, DOCX, PPTX, TXT
        2. **학습 목적** 및 **문제 옵션** 설정
        3. **AI 문제 생성** 클릭
        4. 문제에 **답변 입력** 후 **정답 확인**
        5. 채점 완료 후 **학습 분석** 확인

        ---
        **지원 파일:** PDF, DOCX, PPTX, TXT
        """
    )

    if st.session_state.uploaded_filename:
        st.markdown(f"📄 현재 문서: **{st.session_state.uploaded_filename}**")

    if st.button("🔄 초기화", use_container_width=True):
        for key in DEFAULTS:
            st.session_state[key] = DEFAULTS[key]
        st.rerun()
