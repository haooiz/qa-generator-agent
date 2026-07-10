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
# OPENAI_API_KEY=atl-...
# AZURE_OPENAI_ENDPOINT=https://skax.ai-talentlab.com

# 3. 앱 실행
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 로 접속합니다.

## Streamlit Cloud 배포

1. GitHub 저장소 연결: `https://github.com/haooiz/qa-generator-agent`
2. [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Repository: `haooiz/qa-generator-agent`, Branch: `main`, Main file: `app.py`
4. **Advanced settings → Secrets** 에 아래 입력:

```toml
OPENAI_API_KEY = "atl-..."
AZURE_OPENAI_ENDPOINT = "https://skax.ai-talentlab.com"
AZURE_OPENAI_API_VERSION = "2024-12-01-preview"
OPENAI_MODEL = "gpt-4.1"
```

5. **Deploy** 클릭 → `https://qa-generator-agent.streamlit.app` 형태의 링크 생성

> Streamlit Cloud에는 `.env`가 없습니다. **반드시 Secrets에 API 키**를 등록해야 합니다.  
> 코드 수정 후 GitHub에 push하면 Cloud 앱이 자동으로 재배포됩니다.

## API 키 보안 (배포 전 필수)

공개 Streamlit 링크는 **누구나 API를 호출**할 수 있으므로, OpenAI에서 **전용 키 + 사용 한도**를 설정하세요.

### 1. 전용 API 키 발급

1. [OpenAI API Keys](https://platform.openai.com/api-keys) 접속
2. **Create new secret key** → 이름 예: `qa-generator-과제용`
3. **기존에 노출됐을 수 있는 키는 Revoke(폐기)** 후 새 키만 사용

### 2. 사용 한도 설정

1. [Limits / Billing](https://platform.openai.com/settings/organization/limits) 접속
2. **Monthly budget** — 예: `$5` 또는 `$10` (과제용이면 낮게)
3. 한도 도달 시 **알림 이메일** 켜기
4. (선택) [Usage](https://platform.openai.com/usage)에서 주기적으로 사용량 확인

### 3. 키 등록 위치 (GitHub에는 넣지 않음)

| 환경 | 설정 위치 |
|------|-----------|
| 로컬 PC | 프로젝트 `.env` |
| Streamlit Cloud | 앱 **Settings → Secrets** |

```toml
OPENAI_API_KEY = "sk-새로-발급한-전용-키"
OPENAI_MODEL = "gpt-4o-mini"
```

### 4. 과제 종료 후

- OpenAI에서 해당 키 **Revoke**
- Streamlit Cloud Secrets에서 키 삭제

## 프로젝트 구조

```
├── app.py                 # Streamlit 메인 앱
├── requirements.txt
├── templates/             # 엑셀 출력 서식 템플릿
└── utils/
    ├── document_parser.py # 문서 텍스트 추출
    ├── ai_service.py      # Azure OpenAI API 연동
    ├── prompts.py         # AI 프롬프트
    ├── quiz_helpers.py    # 객관식/OX 채점
    └── export.py          # 엑셀 다운로드
```

## 엑셀 출력

`templates/qa_export_template.xlsx` 에서 열 너비·병합 등 **서식을 Excel로 직접 수정**할 수 있습니다.  
다운로드 시 템플릿에 질문·정답 데이터만 채워집니다.

## 기술 스택

- Python, Streamlit
- Azure OpenAI API (gpt-4.1, skax.ai-talentlab.com)
- pypdf, python-docx, python-pptx, openpyxl
