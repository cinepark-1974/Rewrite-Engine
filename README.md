# 👖 BLUE JEANS REWRITE ENGINE

> **시나리오 분석 · 대사 워싱 · AI 각색 자동화 시스템**  
> Young · Vintage · Free · Innovative

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://rewrite-engine.streamlit.app)

---

## 개요

**REWRITE ENGINE**은 시나리오 PDF를 업로드하면 3명의 AI 비서가 할리우드 표준으로 분석하고, 문제점을 진단하고, 직접 각색 원고를 작성해주는 웹 애플리케이션입니다.

```
PDF 업로드 → CHRIS 분석 → SHIHO 워싱 → MOON 각색 → 보고서 DOCX 다운로드
```

---

## 3비서 시스템

| 비서 | 직책 | 역할 |
|------|------|------|
| 🔍 **CHRIS** | Senior Script Analyst | 구조 분석 · 15-Beat Sheet · 서사동력 · 시각화 · 장르 진단 |
| ✂️ **SHIHO** | Script Doctor | 핵심 문제 진단 · 시퀀스 워싱 · 대사 4축 분석 · 각색 제안 |
| ✍️ **MOON** | Senior Screenwriter | 수정씬 6개 + 추가씬 4개 · 표준 각본 형식 리라이팅 |

---

## 분석 리포트 구성 (12섹션)

1. **종합 분석** — 4축 정밀 평가 (STRUCTURE · HERO · CONCEPT · GENRE) + 최종 점수
2. **로그라인 분석** — 원본 로그라인 → AI 개선 버전
3. **줄거리** — 기승전결 5~7문장 Synopsis
4. **장점 및 보완점** — Pros / Cons / 핵심 처방
5. **서사 동력** — Goal / Lack / Strategy 분석
6. **구성 및 플롯** — 15-Beat Sheet 전체 매핑
7. **시각화** — 긴장도 곡선 + 인물 비중 차트
8. **장르 분석** — 장르 준수도 · 체크리스트 · 누락 요소
9. **시퀀스 워싱** — 6개 시퀀스 진단/처방 카드
10. **대사 워싱** — 3축 점수 (캐릭터 적합성 · 서브텍스트 · 행동/감정/관계) + 개선 제안
11. **각색 제안** — STEP 01~10 구체적 Action Plan
12. **각색 원고** — 수정씬 6개 + 추가씬 4개 BEFORE/AFTER 각본

---

## 시작하기

### 1. 저장소 클론
```bash
git clone https://github.com/cinepark-1974/RewriteEngine.git
cd RewriteEngine
```

### 2. 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. API 키 설정
`.streamlit/secrets.toml` 파일 생성:
```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```

### 4. 실행
```bash
streamlit run main.py
```

---

## Streamlit Cloud 배포

1. GitHub 저장소 연결
2. **Secrets** 탭에 `ANTHROPIC_API_KEY` 등록
3. `.streamlit/config.toml` 확인 (라이트 모드 고정)

```toml
[theme]
base = "light"
primaryColor = "#FFCB05"
backgroundColor = "#FAFAFA"
secondaryBackgroundColor = "#F0F2FF"
textColor = "#1A1A2E"
```

---

## 기술 스택

| 항목 | 내용 |
|------|------|
| 프레임워크 | Streamlit 1.54 (Python) |
| AI 엔진 | Anthropic Claude Opus (claude-opus-4-5) |
| DOCX 생성 | Node.js + docx-js |
| 시각화 | Plotly |
| 배포 | Streamlit Cloud |

---

## 주요 기능

- 📄 **PDF 자동 파싱** — PyPDF2 기반 텍스트 추출
- 🎯 **4축 정밀 평가** — Hollywood Standard 기반 0~10점 채점
- 📊 **긴장도 곡선** — 씬별 텐션 시각화
- 🎭 **대사 4축 분석** — 캐릭터 적합성 · 서브텍스트 · 행동/감정/관계
- ✍️ **AI 각색 원고** — 10개 씬 직접 리라이팅
- 📥 **DOCX 다운로드** — 12섹션 전문 보고서 자동 생성
- 🗂️ **분석 갤러리** — 이전 분석 결과 저장 및 재열람

---

## 사용 흐름

```
1. 시나리오 PDF 업로드
      ↓
2. CHRIS — 약 30~60초
   구조/캐릭터/컨셉/장르 4축 분석
   15-Beat Sheet 자동 매핑
      ↓
3. SHIHO — 약 30~60초
   핵심 문제 진단 및 처방
   대사 품질 3축 평가
      ↓
4. MOON — 약 60~90초
   10개 씬 직접 리라이팅
      ↓
5. DOCX 다운로드
   12섹션 전문 보고서
```

---

## 파일 구조

```
RewriteEngine/
├── main.py              # 메인 앱
├── gen_docx.js          # DOCX 생성 (Node.js)
├── requirements.txt
├── .streamlit/
│   └── config.toml      # 테마 설정
└── README.md
```

---

## 라이선스

© 2026 BLUE JEANS PICTURES. All rights reserved.  
내부 도구 전용. 무단 배포 금지.
