# AI 질의응답 생성기

문서를 업로드하면 AI가 학습용 문제를 생성하고, 답변 채점·학습 분석·엑셀 출력까지 지원하는 Streamlit 웹 앱입니다.

## 개요

학습 자료(PDF, Word, PowerPoint, TXT)를 읽어 **핵심 요약**과 **맞춤형 문제**를 만들고, 사용자가 직접 답한 뒤 **정답 확인**·**취약점 분석**을 제공합니다.  
과제의 **성장 지원 Agent** 컨셉에 맞춰, 채점 결과를 바탕으로 학습 이해도와 추천 복습 영역을 보여 줍니다.

## 주요 기능

| 구분 | 설명 |
|------|------|
| ① 문서 업로드 | PDF, DOCX, PPTX, TXT 지원 |
| ② 문제 생성 | 유형·난이도·문제 수 설정 후 AI 생성 |
| ③ 퀴즈 | 답 입력 → **정답 확인** 후 채점·해설 공개 |
| ④ 성장 지원 | 학습 이해도, 추천 복습, 취약점 분석, 엑셀 다운로드 |

**지원 문제 유형:** 객관식, 주관식, OX, 면접 질문, 서술형

## 실행 방법

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. API 키 설정 (.env.example 참고)
# OPENAI_API_KEY=your_key

# 3. 앱 실행
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 로 접속합니다.

## 프로젝트 구조

```
├── app.py                 # Streamlit 메인 앱
├── requirements.txt
├── templates/             # 엑셀 출력 서식 템플릿
└── utils/
    ├── document_parser.py # 문서 텍스트 추출
    ├── ai_service.py      # OpenAI API 연동
    ├── prompts.py         # AI 프롬프트
    ├── quiz_helpers.py    # 객관식/OX 채점
    └── export.py          # 엑셀 다운로드
```

## 엑셀 출력

`templates/qa_export_template.xlsx` 에서 열 너비·병합 등 **서식을 Excel로 직접 수정**할 수 있습니다.  
다운로드 시 템플릿에 질문·정답 데이터만 채워집니다.

## 기술 스택

- Python, Streamlit
- OpenAI API (gpt-4o-mini)
- pypdf, python-docx, python-pptx, openpyxl
