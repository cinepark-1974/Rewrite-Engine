# 👖 BLUE JEANS SCRIPT DOCTOR : REWRITE ENGINE v2.0

> BLUE JEANS PICTURES · Script Doctoring SaaS  
> 최종 업데이트: 2026-03-15

---

## 1. 제품 개요

REWRITE ENGINE은 시나리오 PDF를 업로드하면 **할리우드 스튜디오 커버리지 수준의 분석 → 정밀 진단 → 실제 삽입 가능한 리라이트**를 3단계로 생성하는 Script Doctoring 엔진이다.

### 핵심 원칙

1. 원고의 결(Voice)을 해치지 않는다.
2. 억지 분량 채우기를 하지 않는다. 모든 리라이트는 명확한 문제 해결 또는 효과 증폭과 연결된다.
3. 모든 판단은 페이지/시퀀스 근거와 연결한다.
4. 장르적 재미(Genre Fun)의 복구가 리라이트의 최우선 목표이다.

---

## 2. v2.0 주요 변경사항 (v1.1 → v2.0)

| 항목 | v1.1 | v2.0 |
|------|------|------|
| 파일 구조 | main.py 단일 파일 (1,862줄) | main.py (1,239줄) + prompt.py (635줄) 분리 |
| 장르 진단 | "장르 적합성 분석해" 단순 지시 | 8장르 Rule Pack (core/must_have/hook/punch/fails/genre_fun) |
| 리라이트 분량 | 150~200자/씬 | 500~800자/씬 + Hook/Punch 필수 |
| 진단↔씬 연결 | 느슨한 연결 | linked_diagnosis (1:1 매핑) |
| 장르 재미 | 미평가 | genre_fun_alive 판정 + genre_fun_recovery 복구 제안 |
| SHIHO→MOON 파이프라인 | 진단/처방만 전달 | problem_types + risk + genre_fix → linked_diagnosis |
| DOCX 생성 | gen_docx.js (Node.js) + python-docx fallback | python-docx 단일 통합 |
| 모델 | claude-opus-4-5 | claude-sonnet-4-20250514 (비용 효율) |
| MOON max_tokens | 12,000 | 16,000 |

---

## 3. 브랜드 철학 : Indigo Spirit

### New and Classic
작가의 젊고 자유로운 상상력(New)을 존중하되, 시간이 지나도 남는 클래식한 깊이(Classic)를 더한다.

### Freedom Fit
규칙을 강요하기보다, 작품이 가장 자연스럽고 아름답게 숨 쉴 수 있는 방향(Fit)을 제안한다.

### Innovative Washing
표면적 문장 손질보다 서사의 불순물(인과, 욕망, 대가, 장면 기능)을 먼저 걷어낸다.

---

## 4. 사용자 플로우

```
PDF 시나리오 업로드
  ↓
🔍 CHRIS — Analysis (구조/장르/인물/비트 진단 + 장르 Rule Pack 적용)
  ↓
🧹 SHIHO — Doctoring (시퀀스 워싱 + 대사 4축 분석 + 장르 재미 복구 제안)
  ↓
✍️ MOON — Rewrite (진단 연결 10개 씬 리라이트 + Hook/Punch)
  ↓
📄 DOCX 보고서 다운로드
```

총 3회 클릭으로 보고서 완성.

---

## 5. 3비서 시스템

| 비서 | 직책 | 역할 |
|------|------|------|
| CHRIS | Senior Script Analyst | 구조 분석 · 15-Beat Sheet · 서사동력 · 장르 Rule Pack 진단 · genre_fun_alive 판정 |
| SHIHO | Script Doctor | 시퀀스 워싱 · 문제유형 진단 · 대사 4축 분석 · 장르 재미 복구 제안 · 각색 제안 10개 |
| MOON | Senior Screenwriter | 진단 연결 리라이팅 · Hook/Punch 필수 · 500~800자 · 수정씬 6 + 추가씬 4 |

---

## 6. 8장르 Rule Pack

각 장르마다 core(핵심 원칙), must_have(필수 요소 4개), hook(씬 시작 패턴), punch(씬 종결 패턴), fails(실패 패턴), genre_fun(장르적 재미의 본질)을 정의한다.

| 장르 | 핵심 | 장르적 재미 |
|------|------|------------|
| 드라마 | 선택과 대가로 진실 도달 | '나라면 어떻게 할까' 고민하게 만드는 것 |
| 느와르 | 도덕적 모호함, 타락과 생존 | 나쁜 줄 알면서도 응원하게 되는 도덕적 긴장 |
| 스릴러 | 정보 비대칭, 시간 압박 | '제발 뒤를 봐!' 속으로 외치게 하는 정보 비대칭 |
| 코미디 | 기대 위반, 반복과 변주 | '저러다 큰일 나겠다'면서 멈출 수 없는 에스컬레이션 |
| 멜로/로맨스 | 갈망 축적, 감정 지연 | 두 사람의 손이 닿기 직전에 숨을 멈추는 감정 지연 |
| 호러 | 공포 예감, 안전감 파괴 | 화면을 가리면서도 손가락 사이로 보게 만드는 공포의 예감 |
| 액션 | 물리적 목표와 대가 | '어떻게 이걸 해결하지?' 조마조마하는 전술적 긴장 |
| SF/판타지 | 세계 규칙 = 인간 드라마 은유 | '이 세계에서는 그게 가능해?'라는 발견의 쾌감 |

---

## 7. SHIHO→MOON 파이프라인 (v2.0 신규)

v2.0의 핵심 개선. SHIHO의 진단이 MOON의 씬 선택에 1:1로 연결된다.

```
SHIHO washing_table
  ├─ seq: "Seq 3"
  ├─ problem_types: ["대립/압박 약함"]
  ├─ diagnosis: "주인공과 빌런의 첫 대면에서 긴장 부족"
  ├─ prescription: "물리적 공간을 밀폐 공간으로 바꿔 압박감 조성"
  ├─ risk: "빌런의 매력이 약화될 수 있음"
  └─ genre_fix: "스릴러의 정보 비대칭을 이 장면에서 구현 가능"
        ↓
MOON rewrite scene
  ├─ linked_diagnosis: "Seq 3: 대립/압박 약함"
  ├─ hook: "밀폐된 엘리베이터, 두 사람만 남는다"
  ├─ punch: "빌런이 문을 잠그며 '이제 솔직해지자'"
  └─ content: 500~800자 각본
```

---

## 8. 분석 리포트 구성 (12섹션)

| # | 섹션 | 내용 |
|---|------|------|
| 1 | 종합 분석 | 4축 정밀 평가 (STRUCTURE · HERO · CONCEPT · GENRE) + Final Score |
| 2 | 로그라인 분석 | Original → Washed Logline |
| 3 | 줄거리 | Synopsis 5~7문장 |
| 4 | 장점 및 보완점 | Pros / Cons / Key Prescription |
| 5 | 서사 동력 | Goal / Lack / Strategy + 평가 |
| 6 | 15-Beat Sheet | 15비트 전체 매핑 |
| 7 | 시각화 | 긴장도 곡선 + 인물 비중 차트 |
| 8 | 장르 분석 | 장르 Rule Pack 기반 진단 + genre_fun 판정 + Hook/Punch 체크 |
| 9-A | 시퀀스 워싱 | 진단/처방/Risk/장르복구 카드 |
| 9-B | 대사 워싱 | 3축 점수 + Before/After |
| 9-C | 장르 재미 복구 | 약한 구간 특정 + Hook/Punch 복구 제안 |
| 10 | 각색 제안 | STEP 01~10 Action Plan |
| 11 | 각색 원고 | 수정씬 6 + 추가씬 4 · linked_diagnosis · Hook/Punch |

---

## 9. 분석 메트릭 (Hollywood Standard)

### 4축 정밀 평가 (0~10)

| 축 | 가중치 | 기준 |
|----|:------:|------|
| STRUCTURE | 0.30 | 인과관계 정밀도, 3막 구조 완성도 |
| HERO | 0.30 | Goal/Need/Strategy, 감정선 선명도 |
| CONCEPT | 0.20 | 하이컨셉, 독창성, 시장성 |
| GENRE | 0.20 | 장르 문법 충실도, 장르적 재미, 필수 요소 충족 |

### Final Score

Final = 0.3 × STRUCTURE + 0.3 × HERO + 0.2 × CONCEPT + 0.2 × GENRE

### Verdict

추천 / 고려 / 비추천 (텍스트 판단 + 근거 3줄)

---

## 10. 문제유형 10개

| # | 유형 |
|---|------|
| 1 | 목표 불명확 |
| 2 | 대가 약함 |
| 3 | 대립/압박 약함 |
| 4 | 인과 붕괴 |
| 5 | 리듬 늘어짐 |
| 6 | 정보 타이밍 문제 |
| 7 | 톤 흔들림 |
| 8 | 캐릭터 불일치 |
| 9 | 회수 부족 |
| 10 | 장면 기능 불명확 |

---

## 11. 디자인 시스템 : The Denim Look

### Color Palette

| 이름 | 코드 | 용도 |
|------|------|------|
| White | #FAFAFA | 배경 |
| Midnight Blue | #191970 | 핵심 텍스트, 차트 |
| Stitch Yellow | #FFCB05 | 하이라이트, 포인트 |
| Green | #2EC484 | 긍정/완료 |
| Red | #FF6432 | 경고/부정 |

### Typography

| 용도 | 폰트 |
|------|------|
| UI/본문 | Pretendard |
| 각본 블록 | Courier New / Courier Prime |

---

## 12. 파일 구조

```
rewrite-engine-v2/
├── main.py              ← Streamlit 메인 앱 (1,239줄)
├── prompt.py            ← System Prompt + Genre Rules + 3 Builders (635줄)
├── requirements.txt     ← streamlit, anthropic, PyPDF2, python-docx, plotly
├── .streamlit/
│   └── config.toml      ← 라이트모드 테마
└── README.md
```

### prompt.py 구조

| 요소 | 설명 |
|------|------|
| SYSTEM_PROMPT | 브랜드 철학 + 출력 규칙 + 안전 규칙 |
| GENRE_RULES | 8장르 딕셔너리 (core/must_have/hook/punch/fails/genre_fun) |
| GENRE_KEYWORD_MAP | 장르 키워드 → 장르키 매핑 |
| detect_genre_key() | 장르 문자열 자동 감지 |
| get_genre_rules_block() | 장르 Rule Pack → 프롬프트 텍스트 변환 |
| build_analysis_prompt() | CHRIS 분석 프롬프트 빌더 |
| build_doctoring_prompt() | SHIHO 워싱 프롬프트 빌더 |
| build_rewrite_prompt() | MOON 리라이트 프롬프트 빌더 |
| get_report_filename() | DOCX 파일명 생성 |

### main.py 구조

| 섹션 | 내용 |
|------|------|
| [0] 페이지 설정 | st.set_page_config + session_state 초기화 |
| [1] 디자인 시스템 | CSS + 컬러 상수 |
| [2] SVG 아바타 | CHRIS/SHIHO/MOON 인라인 SVG |
| [3] 유틸리티 | safe(), parse_json(), get_client(), call_claude() |
| [4] PDF 추출 | PyPDF2 텍스트 추출 |
| [5] AI 실행 | run_chris(), run_shiho(), run_moon() — prompt.py 연동 |
| [6] 렌더러: Analysis | 종합/로그라인/줄거리/장단점/서사동력/Beat/시각화/장르 |
| [7] 렌더러: Washing | 시퀀스 워싱 + 대사 워싱 + 장르 재미 복구 |
| [8] 렌더러: Rewriting | 각색 원고 + linked_diagnosis + Hook/Punch |
| [9] DOCX 생성 | python-docx 통합 (gen_docx.js 제거) |
| [10~14] UI | 진행바 + 비서카드 + 워크스페이스 + 갤러리 + 실행 |

---

## 13. 실행 환경

| 항목 | 값 |
|------|------|
| Python | 3.9+ |
| streamlit | ≥1.30 |
| anthropic | ≥0.40 |
| python-docx | ≥1.0 |
| PyPDF2 | ≥3.0 |
| plotly | ≥5.0 |
| AI 모델 | claude-sonnet-4-20250514 |
| API KEY | ANTHROPIC_API_KEY (Streamlit secrets) |
| 배포 | Streamlit Cloud + GitHub |

### 모델 변경

Opus로 변경하려면 main.py의 call_claude() 함수에서 모델명만 수정:

```python
model="claude-opus-4-5-20250414"
```

---

## 14. Safety & Content

허용: 허구 속 범죄/폭력/살인/마약/납치, 성적 긴장, 거친 언어
운영: 드라마 기능 우선. 수법보다 인물/대가/윤리성
금지: 현실 범죄 실행 지침, 제조법, 고어 자체 목적

---

## 15. QA 체크리스트

1. 첫 30초 안에 Verdict가 보이는가
2. 장르 Rule Pack 기반 진단이 구체적인가
3. genre_fun_alive 판정이 정확한가
4. washing_table의 problem_types가 10개 유형 내에 있는가
5. SHIHO의 genre_fun_recovery가 구체적 시퀀스를 특정하는가
6. MOON의 모든 씬에 linked_diagnosis가 있는가
7. 모든 씬에 Hook과 Punch가 명시되었는가
8. 각 씬이 500자 이상인가
9. DOCX 보고서가 정상 생성되는가
10. 전체 톤이 "세계 수준의 스튜디오 커버리지"처럼 느껴지는가

---

## 16. 라이선스

© 2026 BLUE JEANS PICTURES. All rights reserved.
내부 도구 전용. 무단 배포 금지.

---

*End of Document*
