# =================================================================
# writer_link.py — Writer Engine 세션 JSON 연계 (v2.3)
#
# 목적
#   Writer Engine이 비트별로 이미 산출한 GENRE_BOOSTER_CHECK 데이터를
#   Rewrite Engine의 장르 정밀 진단(G1 웃음 밀도 / G2 3막 유지율 / G4 출처 분포)의
#   보조 근거로 끌어온다. 재계산 없이 기존 산출물을 재사용하는 것이 목적이다.
#
# 중요 — 엔진 본질 보호
#   Writer 세션 JSON은 "비트 설계 단계" 산출물이다. 분석 대상(시나리오)이 아니다.
#   따라서 이 데이터는 진단의 참조 자료로만 쓰이고, 시나리오 본문을 대체하지 않는다.
#   씬 번호 기준 판정의 최종 권위는 항상 업로드된 시나리오 PDF에 있다.
# =================================================================

import re
import json

# 15-Beat → 막 매핑 (Blake Snyder 기준)
ACT_MAP = {
    1: "1막", 2: "1막", 3: "1막", 4: "1막", 5: "1막",
    6: "2막", 7: "2막", 8: "2막", 9: "2막", 10: "2막", 11: "2막",
    12: "3막", 13: "3막", 14: "3막", 15: "3막",
}

_BOOSTER_BLOCK = re.compile(r"<GENRE_BOOSTER_CHECK>(.*?)</GENRE_BOOSTER_CHECK>", re.S)
_RULE_LINE = re.compile(
    r"□\s*룰\s*(\d+)\s*:\s*\[([^\]]+)\]\s*[—\-–]\s*(충족|미충족)\s*(?:/\s*(.*))?"
)
_MET_COUNT = re.compile(r"충족\s*개수\s*:\s*(\d+)\s*개\s*/\s*(\d+)\s*개")
_REQUIRED = re.compile(r"필수\s*충족\s*개수\s*:\s*(\d+)\s*개")


def _to_int(v, default=0):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return default


def parse_booster_block(text: str) -> dict:
    """비트 본문 텍스트 하나에서 GENRE_BOOSTER_CHECK 블록을 구조화."""
    if not isinstance(text, str):
        return {}
    m = _BOOSTER_BLOCK.search(text)
    if not m:
        return {}
    body = m.group(1)

    rules = []
    for rm in _RULE_LINE.finditer(body):
        rules.append({
            "no": _to_int(rm.group(1)),
            "name": (rm.group(2) or "").strip(),
            "met": rm.group(3) == "충족",
            "evidence": (rm.group(4) or "").strip(),
        })

    met = total = required = 0
    cm = _MET_COUNT.search(body)
    if cm:
        met, total = _to_int(cm.group(1)), _to_int(cm.group(2))
    else:
        met = len([r for r in rules if r["met"]])
        total = len(rules)
    rq = _REQUIRED.search(body)
    if rq:
        required = _to_int(rq.group(1))

    return {
        "rules": rules,
        "met": met,
        "total": total,
        "required": required,
        "passed": (met >= required) if required else None,
    }


def parse_writer_session(raw) -> dict:
    """Writer Engine 세션 JSON(dict 또는 JSON 문자열/바이트) → 참조 데이터.

    반환 dict의 ok=False면 message에 실패 이유가 담긴다.
    """
    # ── 입력 정규화 ──
    data = raw
    if isinstance(raw, (bytes, bytearray)):
        try:
            data = json.loads(raw.decode("utf-8"))
        except Exception as e:
            return {"ok": False, "message": f"JSON 해석 실패: {type(e).__name__}"}
    elif isinstance(raw, str):
        try:
            data = json.loads(raw)
        except Exception as e:
            return {"ok": False, "message": f"JSON 해석 실패: {type(e).__name__}"}
    if not isinstance(data, dict):
        return {"ok": False, "message": "최상위가 JSON 객체가 아닙니다."}

    meta = data.get("_meta", {})
    meta = meta if isinstance(meta, dict) else {}
    session = data.get("session", {})
    session = session if isinstance(session, dict) else {}

    beats_done = session.get("beats_done", {})
    if not isinstance(beats_done, (dict, list)) or not beats_done:
        return {"ok": False,
                "message": "Writer Engine 세션 JSON이 아닌 것 같습니다 (session.beats_done 없음)."}

    # ── 비트별 파싱 ──
    if isinstance(beats_done, dict):
        pairs = []
        for k, v in beats_done.items():
            pairs.append((_to_int(k, 0), v))
        pairs.sort(key=lambda x: x[0])
    else:
        pairs = [(i + 1, v) for i, v in enumerate(beats_done)]

    beats = []
    for bno, body in pairs:
        text = body if isinstance(body, str) else json.dumps(body, ensure_ascii=False)
        parsed = parse_booster_block(text)
        beats.append({
            "beat": bno,
            "act": ACT_MAP.get(bno, "2막"),
            "has_booster": bool(parsed),
            "rules": parsed.get("rules", []),
            "met": parsed.get("met", 0),
            "total": parsed.get("total", 0),
            "required": parsed.get("required", 0),
            "passed": parsed.get("passed"),
        })

    scored = [b for b in beats if b["has_booster"] and b["total"]]

    # ── 막별 웃음 장치 충족률 (G1 / G2 보조 근거) ──
    act_stats = {}
    for act in ("1막", "2막", "3막"):
        rows = [b for b in scored if b["act"] == act]
        if rows:
            met_sum = sum(b["met"] for b in rows)
            tot_sum = sum(b["total"] for b in rows)
            act_stats[act] = {
                "beats": len(rows),
                "met_sum": met_sum,
                "total_sum": tot_sum,
                "avg_met": round(met_sum / len(rows), 2),
                "fill_ratio": round(met_sum / tot_sum, 3) if tot_sum else 0.0,
            }

    retention = None
    if "1막" in act_stats and "3막" in act_stats:
        a1 = act_stats["1막"]["avg_met"]
        a3 = act_stats["3막"]["avg_met"]
        if a1:
            retention = round(a3 / a1, 3)

    # ── 룰별 충족 통계 (G4 출처 편중 보조 근거) ──
    rule_stats = {}
    for b in scored:
        for r in b["rules"]:
            name = r["name"] or f"룰 {r['no']}"
            slot = rule_stats.setdefault(name, {"met": 0, "seen": 0, "missing_beats": []})
            slot["seen"] += 1
            if r["met"]:
                slot["met"] += 1
            else:
                slot["missing_beats"].append(b["beat"])
    for name, slot in rule_stats.items():
        slot["ratio"] = round(slot["met"] / slot["seen"], 3) if slot["seen"] else 0.0

    # ── 경고 (장르 조회 폴백 등) ──
    warnings = []
    ge = session.get("genre_essence", {})
    ge = ge if isinstance(ge, dict) else {}
    ge_source = str(ge.get("source", ""))
    if "fallback" in ge_source.lower():
        warnings.append(
            f"Writer Engine 측 장르 조회가 폴백되었습니다 "
            f"(source: {ge_source} / fun_engine: {ge.get('fun_engine','')}). "
            f"이 세션의 비트는 해당 장르 기준으로 평가되었을 수 있어, 충족 데이터를 그대로 신뢰하지 마십시오."
        )
    unscored = [b["beat"] for b in beats if not b["has_booster"]]
    if unscored:
        warnings.append(f"장르 부스터 데이터가 없는 비트: {', '.join(str(b) for b in unscored)}")

    return {
        "ok": True,
        "source": "writer_engine_session",
        "title": str(session.get("title", "") or meta.get("title", "")),
        "genre": str(meta.get("genre", "") or session.get("genre", "")),
        "logline": str(session.get("logline", "")),
        "beat_count": len(beats),
        "scored_beat_count": len(scored),
        "beats": beats,
        "act_stats": act_stats,
        "act3_retention": retention,
        "rule_stats": rule_stats,
        "genre_essence": {
            "fun_engine": str(ge.get("fun_engine", "")),
            "absolute_goal": str(ge.get("absolute_goal", "")),
            "source": ge_source,
        },
        "warnings": warnings,
    }


def build_writer_reference_block(ref: dict) -> str:
    """파싱 결과 → CHRIS 프롬프트 주입용 참조 블록.
    분석 대상이 아니라 보조 근거임을 명시한다."""
    if not isinstance(ref, dict) or not ref.get("ok"):
        return ""
    scored = [b for b in ref.get("beats", []) if b.get("has_booster")]
    if not scored:
        return ""

    beat_lines = []
    for b in scored:
        miss = [r["name"] for r in b.get("rules", []) if not r.get("met")]
        line = f"  Beat {b['beat']} ({b['act']}): 웃음 장치 {b['met']}/{b['total']} 충족"
        if miss:
            line += f" — 미작동: {', '.join(miss)}"
        beat_lines.append(line)

    act_lines = []
    for act, s in ref.get("act_stats", {}).items():
        act_lines.append(
            f"  {act}: 비트 {s['beats']}개 / 비트당 평균 충족 {s['avg_met']}개 / 충족률 {s['fill_ratio']*100:.0f}%"
        )

    ret = ref.get("act3_retention")
    ret_line = ""
    if ret is not None:
        ret_line = (f"\n[3막 유머 유지율 (Writer 실측)]\n"
                    f"  1막 대비 3막 웃음 장치 밀도 = {ret*100:.0f}%")

    weak_rules = sorted(
        [(n, s) for n, s in ref.get("rule_stats", {}).items() if s.get("seen")],
        key=lambda x: x[1].get("ratio", 0)
    )[:4]
    rule_lines = [
        f"  {n}: 충족률 {s['ratio']*100:.0f}% ({s['met']}/{s['seen']})"
        + (f" — 미작동 비트 {', '.join(str(b) for b in s['missing_beats'][:8])}" if s.get("missing_beats") else "")
        for n, s in weak_rules
    ]

    warn_block = ""
    if ref.get("warnings"):
        warn_block = "\n[주의]\n" + "\n".join([f"  ⚠️ {w}" for w in ref["warnings"]])

    return f"""[Writer Engine 참조 데이터 — 보조 근거]
같은 작품의 비트 설계 단계에서 이미 산출된 장르 부스터 판정 데이터다.
이것은 분석 대상이 아니라 참조 자료다. 씬 단위 판정의 최종 권위는 업로드된 시나리오 본문에 있다.
본문과 이 데이터가 어긋나면 본문을 따르고, 어긋난 사실 자체를 진단에 기록하라.
(예: 설계 단계에는 웃음 장치가 있었는데 원고에서 사라졌다면 그것이 곧 진단 대상이다.)

작품: {ref.get('title','')} / 장르(Writer 기록): {ref.get('genre','')}
부스터 데이터 보유 비트: {len(scored)} / {ref.get('beat_count',0)}

[비트별 웃음 장치 충족]
{chr(10).join(beat_lines)}

[막별 집계]
{chr(10).join(act_lines) if act_lines else '  (집계 불가)'}
{ret_line}

[만성 미작동 장치 — 출처 편중 판단에 참고]
{chr(10).join(rule_lines) if rule_lines else '  (해당 없음)'}
{warn_block}

[활용 지침]
- G1(웃음 밀도), G2(3막 유지율), G4(출처 분포) 판정 시 위 수치를 근거로 인용하라.
- 인용할 때는 "Writer 설계 기준"임을 명시하고, 원고 실측값과 나란히 제시하라.
"""


def summarize_writer_ref(ref: dict) -> dict:
    """UI 표시용 요약 (숫자 몇 개만)"""
    if not isinstance(ref, dict) or not ref.get("ok"):
        return {}
    ret = ref.get("act3_retention")
    return {
        "title": ref.get("title", ""),
        "genre": ref.get("genre", ""),
        "beat_count": ref.get("beat_count", 0),
        "scored_beat_count": ref.get("scored_beat_count", 0),
        "act3_retention_pct": (round(ret * 100) if ret is not None else None),
        "warning_count": len(ref.get("warnings", [])),
    }
