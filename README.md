# 👖 BLUE JEANS REWRITE ENGINE

> **시나리오 분석 · 진단 · AI 각색 자동화 시스템 · v2.2**
> Young · Vintage · Free · Innovative

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://rewrite-engine.streamlit.app)

---

## 개요

**REWRITE ENGINE**은 시나리오 PDF를 업로드하면 3명의 AI 비서가 할리우드 표준으로 분석하고, 작가의 원고를 존중하며 문제점을 진단하고, 직접 각색 원고까지 작성해주는 웹 애플리케이션입니다.

```
PDF 업로드 → CHRIS 분석 → SHIHO 진단 → MOON 리라이트 → 단계별 DOCX 다운로드
```

### Indigo Spirit — 브랜드 철학

1. **New and Classic** — 작가의 젊고 자유로운 상상력(New)을 존중하되, 시간이 지나도 남는 깊이(Classic)를 더한다.
2. **Freedom Fit** — 규칙 강요가 아닌, 작품이 가장 자연스럽게 숨 쉴 수 있는 방향(Fit)을 제안한다.
3. **Innovative Washing** — 표면적 문장 손질보다, 서사의 불순물(인과·욕망·대가·장면기능)을 먼저 걷어낸다.

### Voice First — 리라이트 원칙

리라이트는 "원본의 강점을 보존하면서 약점만 교체"하는 것이지, "원본을 요약해서 다시 쓰는 것"이 아니다. 작가가 이미 잘 쓴 디테일·이미지·리듬·행동 묘사는 절대 삭제하지 않는다.

---

## 3비서 시스템

| 비서 | 직책 | 역할 | 모델 |
|------|------|------|------|
| 🔍 **CHRIS** | Senior Script Analyst | 구조 분석 · 15-Beat Sheet · 서사 동력 · 시각화 · 장르 진단 · 오프닝 기법 역추적 | Opus |
| 🧹 **SHIHO** | Script Doctor | 시퀀스 워싱 · 문제 유형 진단 · 대사 4축 분석 · 각색 제안 · 오프닝 교정 처방 | Opus |
| ✍️ **MOON** | Senior Screenwriter | 수정씬 6개 + 추가씬 4개 · 표준 각본 형식 리라이팅 · 작가 의도 존중 | Opus |

---

## 분석 리포트 구성 (섹션 1~12)

| # | 섹션 | 담당 |
|---|------|------|
| 1 | **종합 분석** — 4축 정밀 평가 (STRUCTURE · HERO · CONCEPT · GENRE) + 최종 점수 | CHRIS |
| 2 | **로그라인 분석** — 원본 로그라인 → AI 개선 버전 | CHRIS |
| 3 | **줄거리** — 기승전결 5~7문장 Synopsis | CHRIS |
| 4 | **장점 및 보완점** — Pros / Cons / 핵심 처방 | CHRIS |
| 5 | **서사 동력** — Goal / Lack / Strategy 분석 | CHRIS |
| 6 | **구성 및 플롯** — 15-Beat Sheet 전체 매핑 | CHRIS |
| 7 | **시각화** — 긴장도 곡선 + 인물 비중 차트 | CHRIS |
| 8 | **장르 분석** — 장르 준수도 · 필수 요소 체크 · 실패 패턴 · Hook/Punch | CHRIS |
| **8-B** | **오프닝 마스터리** — 기법 역추적 · 장르 DNA 일치도 · 도파민 6감각 진단 | CHRIS |
| **8-C** | **오프닝 교정 처방** — 작가 의도 존중형 RX · 완성도 방안 · 도파민 보강 | SHIHO |
| 9 | **시퀀스 워싱** — 최대 10개 시퀀스 진단/처방 카드 | SHIHO |
| 10 | **대사 워싱** — 3축 점수 + Before/After 개선 제안 | SHIHO |
| 11 | **각색 제안** — STEP 01~10 구체적 Action Plan | SHIHO |
| 12 | **각색 원고** — 수정씬 6개 + 추가씬 4개 BEFORE/AFTER 각본 | MOON |

---

## OPENING MASTERY 모듈

v2.2의 핵심 신규 모듈. 오프닝이 관객 뇌에 꽂히는가를 정밀 진단합니다.

### 오프닝 6기법
`ACTION_DROP` · `COLD_OPEN` · `TEASE_REVEAL` · `IN_MEDIA_RES` · `CHARACTER_REVEAL_ACTION` · `HOOK_DIALOGUE`

### 장르별 오프닝 DNA 8종
드라마 · 느와르 · 스릴러 · 코미디 · 멜로/로맨스 · 호러 · 액션 · SF/판타지 — 장르마다 권장 기법과 피해야 할 패턴이 다릅니다.

### 도파민 6감각
충격 · 웃음 · 긴장 · 경이 · 호기심 · 감정 울림 — 장르 DNA가 요구하는 감각이 실제 작동하는지 0~10점으로 채점.

### 진단 · 교정 철학

- **CHRIS (역추적)**: 작가가 어느 기법을 노렸는지 판단 → 장르 DNA와 일치하는지 채점
- **SHIHO (교정)**: 작가 의도 존중 — 기법은 유지하되 완성도만 끌어올림
- **MOON (리라이트)**: `preserve_from_original` 항목은 절대 삭제하지 않음

### 복합 장르의 법칙
"두 번째 장르 = 본질" — 로맨스 스릴러라면 스릴러 DNA로 오프닝을 열어야 본질이 산다.

---

## 🆕 3단계 다운로드 (v2.2)

각 에이전트 완료 시점에 해당 단계까지의 결과물을 즉시 받을 수 있습니다.

```
CHRIS 완료 직후  → 📄 CHRIS 분석 리포트 (섹션 1~8-B)
                    ↓
SHIHO 완료 직후  → 📄 진단·처방 리포트 (섹션 1~11, MOON 제외)
                    ↓
MOON 완료 직후   → 📄 최종 통합 보고서 (섹션 1~12, 전체)
```

### 용도별 권장

| 용도 | 권장 다운로드 |
|------|--------------|
| 초기 스크리닝 · 투자 검토 · 작품 판독 | CHRIS 분석 리포트 |
| 작가 피드백 · 다음 엔진(Revise Engine) 입력 | 진단·처방 리포트 |
| 최종 전달물 · 제작팀 공유 | 최종 통합 보고서 |

### 파일명 자동 구분

- `시나리오분석_{제목}_CHRIS.docx`
- `시나리오진단처방_{제목}_CHRIS+SHIHO.docx`
- `시나리오최종보고서_{제목}_Blue.docx`

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
4. `packages.txt`에 `nodejs`, `npm` 명시 (DOCX 생성용)

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
| AI 엔진 | Anthropic Claude Opus (`claude-opus-4-6`) |
| DOCX 생성 | Node.js + docx-js (fallback: python-docx) |
| PDF 파싱 | PyPDF2 |
| 시각화 | Plotly |
| 배포 | Streamlit Cloud |

---

## 주요 기능

- 📄 **PDF 자동 파싱** — PyPDF2 기반 텍스트 추출
- 🎯 **4축 정밀 평가** — Hollywood Standard 기반 0~10점 채점
- 🎬 **OPENING MASTERY** — 장르 DNA 기반 오프닝 기법 역추적 + 도파민 6감각 진단
- 📊 **긴장도 곡선** — 씬별 텐션 시각화
- 🎭 **대사 4축 분석** — 캐릭터 적합성 · 서브텍스트 · 행동/감정/관계
- ✏️ **작가 의도 존중 교정** — Voice First 원칙 기반 리라이트 처방
- ✍️ **AI 각색 원고** — 10개 씬 직접 리라이팅
- 📥 **3단계 DOCX 다운로드** — CHRIS / SHIHO / MOON 각 단계별 보고서
- 🗂️ **분석 갤러리** — 이전 분석 결과 저장 및 재열람

---

## 사용 흐름

```
1. 시나리오 PDF 업로드
      ↓
2. CHRIS — 약 30~60초
   구조/캐릭터/컨셉/장르 4축 분석 + 15-Beat Sheet + 오프닝 마스터리 역추적
      ↓ [📄 CHRIS 분석 리포트 다운로드 가능]
      ↓
3. SHIHO — 약 30~60초
   시퀀스 워싱 + 대사 4축 진단 + 오프닝 교정 처방
      ↓ [📄 진단·처방 리포트 다운로드 가능]
      ↓
4. MOON — 약 60~90초
   작가 의도 존중형 10개 씬 리라이팅
      ↓
5. 📄 최종 통합 보고서 다운로드 (섹션 1~12 전체)
```

---

## 파일 구조

```
RewriteEngine/
├── main.py              # Streamlit 웹앱 (v2.2)
├── prompt.py            # 3-agent 프롬프트 빌더 + OPENING MASTERY 모듈
├── gen_docx.js          # DOCX 생성 (Node.js + docx-js)
├── requirements.txt     # Python 패키지
├── packages.txt         # 시스템 패키지 (nodejs, npm)
├── .streamlit/
│   └── config.toml      # 테마 설정 (라이트 모드)
└── README.md            # 본 문서
```

### prompt.py — 내부 구조

| 모듈 | 역할 |
|------|------|
| `SYSTEM_PROMPT` | 3-agent 공통 시스템 프롬프트 (Indigo Spirit + Voice First) |
| `GENRE_RULES` | 8장르 Rule Pack (드라마 · 느와르 · 스릴러 · 코미디 · 멜로/로맨스 · 호러 · 액션 · SF/판타지) |
| `OPENING_TECHNIQUES` | 오프닝 6기법 정의 |
| `OPENING_DNA` | 장르별 오프닝 DNA 8종 |
| `DOPAMINE_SIX_SENSES` | 도파민 6감각 정의 |
| `COMPLEX_GENRE_LAW` | 복합 장르 "두 번째 장르 = 본질" 법칙 |
| `build_analysis_prompt()` | CHRIS 프롬프트 빌더 (역추적 진단형) |
| `build_doctoring_prompt()` | SHIHO 프롬프트 빌더 (작가 의도 존중형) |
| `build_rewrite_prompt()` | MOON 프롬프트 빌더 (OPENING RX 최상위 규칙) |

---

## 버전 히스토리

### v2.2 (현재)
- 3단계 다운로드 기능 (CHRIS / SHIHO / MOON 각 단계별 DOCX)
- 8-B, 8-C 섹션 HTML 렌더링 안정화 (f-string 삼항연산자 버그 수정)
- 세션 캐시 기반 성능 최적화

### v2.1
- OPENING MASTERY 모듈 이식 (Creator/Writer Engine 연동)
- 오프닝 6기법 + 장르 DNA 8종 + 도파민 6감각
- CHRIS 에러 3곳 수정 (beats 렌더링 / characters 차트 / drive.evaluation 방어)

### v2.0
- prompt.py 분리 (모듈 구조 확립)
- 8장르 Rule Pack 도입
- 대사 4축 분석
- Voice First 원칙 정립

---

## 라이선스

© 2026 BLUE JEANS PICTURES. All rights reserved.
내부 도구 전용. 무단 배포 금지.
