# genre_profiles — 장르 정밀 진단 프로파일

이 폴더의 `.json` 파일 한 개가 장르 하나의 진단 기준입니다.
코드를 고치지 않고 이 폴더에 파일을 추가하면 그 장르의 정밀 진단축이 활성화됩니다.

## 규칙

- 파일명은 자유. 단 `_`로 시작하는 파일은 읽지 않습니다 (`_TEMPLATE.json`은 견본이므로 무시됨).
- `aliases`에 적힌 문자열이 CHRIS가 판정한 장르명에 포함되면 그 프로파일이 적용됩니다.
- 프로파일이 없는 장르는 기존 8장르 Rule Pack만으로 진단하며, 보고서에 `source: fallback`으로 표시됩니다.

## 필수 필드

| 필드 | 설명 |
|---|---|
| `profile_id` | 영문 소문자 식별자. 보고서·JSON에 그대로 기록됩니다 |
| `genre_label` | 사람이 읽는 장르명 (예: 로맨틱 코미디) |
| `aliases` | 이 장르로 판정할 문자열 목록 |
| `primary_genre_key` | 기존 8장르 중 본질에 해당하는 키 (복합 장르는 두 번째 장르) |
| `base_genre_keys` | 참조할 8장르 Rule Pack 키 목록 |
| `diagnostic_axes` | CHRIS가 채점할 하위 진단축 (G1, G2, ...) |
| `dialogue_axes` | SHIHO가 추가로 볼 대사축 (④, ⑤, ...) |
| `thresholds` | 판정 기준값 |
| `must_have` / `fails` | 장르 필수 요소 / 실패 패턴 |
| `prescription_balance` | 처방 균형 게이트 (하한 비율, 재시도 여부) |
| `protected_asset_rule` | 보호 자산 지정 규칙 |

## 기준값의 출처

`thresholds`는 이론이 아니라 실측에서 나와야 합니다.
`reference_works`에 참조 작품(같은 장르 장편 3~5편)의 씬별 데이터를 한 번 수기로 태깅해두면
이후 모든 진단의 비교 기준이 됩니다.

현재 등록된 프로파일: `romantic_comedy.json`
