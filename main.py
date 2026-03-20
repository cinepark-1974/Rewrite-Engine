# =================================================================
# 👖 BLUE JEANS SCRIPT DOCTOR : REWRITE ENGINE v2.0
# main.py — Streamlit Main App
# =================================================================
# © 2026 BLUE JEANS PICTURES. All rights reserved.

import streamlit as st
import anthropic
from PyPDF2 import PdfReader
import json, re, html, io
import plotly.express as px
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

from prompt import (
    build_analysis_prompt,
    build_doctoring_prompt,
    build_rewrite_prompt,
    get_report_filename,
    GENRE_RULES,
    detect_genre_key,
)

# =================================================================
# 모델 설정 — Writer Engine과 동일 정책
# =================================================================
ANTHROPIC_MODEL_WRITE = "claude-opus-4-6"      # 집필 (MOON 리라이팅) — 최고 품질
ANTHROPIC_MODEL_PLAN  = "claude-sonnet-4-6"    # 분석 (CHRIS, SHIHO) — 비용 효율

# =================================================================
# [0] 페이지 설정 & 세션 초기화
# =================================================================
st.set_page_config(
    page_title="BLUE JEANS REWRITE ENGINE",
    layout="wide",
    page_icon="👖"
)

for k, v in {
    "page": "index",
    "db": [],
    "selected_item": None,
    "step": 0,
    "raw_text": None,
    "analysis": None,
    "washing": None,
    "rewriting": None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# =================================================================
# [1] 디자인 시스템 — The Denim Look
# =================================================================
# 컬러 상수
C_WHITE      = "#FAFAFA"
C_NAVY       = "#191970"
C_YELLOW     = "#FFCB05"
C_GREEN      = "#2EC484"
C_RED        = "#FF6432"
C_BG_LIGHT   = "#F0F2FF"
C_BG_CARD    = "#FFFFFF"
C_BORDER     = "#E6E9EF"

def get_genre_img_url(item):
    """장르별 Picsum Photos 이미지"""
    genre_raw = item.get('genre', {})
    if isinstance(genre_raw, dict):
        genre_str = genre_raw.get('primary', '') + ' ' + ' '.join(genre_raw.get('tags', []))
    else:
        genre_str = str(genre_raw)
    genre_str = genre_str.lower()
    genre_ids = {
        'romance': [1024, 488, 429], 'action': [1036, 373, 412],
        'comedy': [1082, 247, 669], 'horror': [1067, 167, 202],
        'fantasy': [1019, 325, 462], 'family': [1060, 219, 342],
        'crime': [1043, 110, 164], 'history': [1029, 145, 271],
        'drama': [1062, 232, 366],
    }
    mapping = [
        (['로맨스','romance','멜로','love','로코'], 'romance'),
        (['액션','action','스릴러','thriller'], 'action'),
        (['코미디','comedy'], 'comedy'),
        (['공포','horror','호러'], 'horror'),
        (['sf','sci-fi','판타지','fantasy'], 'fantasy'),
        (['가족','family','성장'], 'family'),
        (['범죄','crime','누아르','noir','느와르'], 'crime'),
        (['전쟁','war','역사','historical'], 'history'),
        (['드라마','drama'], 'drama'),
    ]
    genre_key = 'drama'
    for keys, gkey in mapping:
        if any(k in genre_str for k in keys):
            genre_key = gkey
            break
    title = item.get('title', 'film')
    ids = genre_ids[genre_key]
    img_id = ids[abs(hash(title)) % len(ids)]
    return f"https://picsum.photos/id/{img_id}/400/200"


def apply_design():
    st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    @import url('https://cdn.jsdelivr.net/gh/projectnoonnu/2408-3@latest/Paperlogy.css');
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&display=swap');
    :root {
        color-scheme: light only !important;
        --display: 'Playfair Display', 'Paperlogy', 'Georgia', serif;
        --heading: 'Paperlogy', 'Pretendard', sans-serif;
    }
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"],
    [data-testid="stMain"], [data-testid="stMainBlockContainer"],
    [data-testid="block-container"], body { background-color: #FAFAFA !important; }
    html, body, .stApp, p, span, h1, h2, h3, h4, h5, label, li, td, th, div {
        color: #191970 !important;
        font-family: 'Pretendard', sans-serif !important;
    }
    [data-testid="stSidebar"] { display: none !important; }
    th[style*="background:#191970"], thead tr[style*="background:#191970"] th {
        color: #FFCB05 !important; background: #191970 !important;
    }
    [data-testid="stExpander"] details summary {
        background: #F0F2FF !important; border-radius: 8px !important;
        padding: 10px 16px !important; border: 1px solid #E0E4F0 !important;
    }
    [data-testid="stExpander"] details[open] summary {
        border-radius: 8px 8px 0 0 !important; border-bottom: 1px solid #FFCB05 !important;
    }
    [data-testid="stExpander"] summary svg { color: #191970 !important; }
    [data-testid="stExpander"] details > div {
        border: 1px solid #E0E4F0 !important; border-top: none !important;
        border-radius: 0 0 8px 8px !important; padding: 16px !important; background: #FAFAFA !important;
    }
    .header {
        font-size: 0.85rem; font-weight: 700; color: #191970;
        letter-spacing: 0.15em; margin-bottom: 0;
        font-family: 'Paperlogy', 'Pretendard', sans-serif;
    }
    .brand-title {
        font-size: 2.6rem; font-weight: 900; color: #191970;
        font-family: 'Playfair Display', 'Paperlogy', 'Georgia', serif;
        letter-spacing: -0.02em; margin-bottom: 0.15rem;
        position: relative; display: inline-block;
    }
    .sub {
        font-size: 0.72rem; font-weight: 600; letter-spacing: 0.18em;
        color: #8E8E99; margin-top: 0.1rem;
    }
    .agent-card {
        background: #FFFFFF; border: 1px solid #E6E9EF; border-radius: 16px;
        padding: 24px 28px; margin-bottom: 20px; position: relative;
        overflow: hidden; box-shadow: 0 2px 12px rgba(25,25,112,0.06);
    }
    .agent-card::before {
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px;
        background: linear-gradient(90deg, #FFCB05, #191970);
    }
    .agent-card.active { border-color: #FFCB05; box-shadow: 0 4px 20px rgba(255,203,5,0.2); }
    .agent-card.done { border-color: #B8E6D4; }
    .agent-card.waiting { opacity: 0.42; }
    .report-card {
        background: #FFFFFF !important; border: 1px solid #E6E9EF !important;
        border-left: 5px solid #FFCB05 !important; border-radius: 12px !important;
        padding: 22px !important; margin-bottom: 16px !important;
        box-shadow: 0 2px 8px rgba(25,25,112,0.04) !important;
    }
    .report-card h3 {
        color: #191970 !important; font-size: 0.95rem !important;
        font-weight: 800 !important; margin-bottom: 14px !important;
    }
    div.stButton > button {
        background: #FFCB05 !important; color: #191970 !important;
        font-weight: 900 !important; border-radius: 10px !important; border: none !important;
    }
    div.stButton > button:hover { background: #191970 !important; color: #FFFFFF !important; }
    .step-bar { display:flex; align-items:center; justify-content:center; gap:0; margin:24px 0; }
    .step-dot { width:34px; height:34px; border-radius:50%; display:flex;
        align-items:center; justify-content:center; font-weight:900; font-size:0.8rem; }
    .step-dot.done { background:#2EC484; color:#FFFFFF; }
    .step-dot.active { background:#FFCB05; color:#191970; }
    .step-dot.wait { background:#E6E9EF; color:#AAAAAA; }
    .step-line { flex:1; height:2px; background:#E6E9EF; }
    .step-line.done { background:#2EC484; }
    .gallery-card { background:#FFFFFF; border:1px solid #E6E9EF; border-radius:14px;
        overflow:hidden; text-align:center; box-shadow:0 2px 8px rgba(25,25,112,0.04); }
    .gallery-card-img { width:100%; height:140px; object-fit:cover; display:block; background:#E6E9EF; }
    .gallery-card-body { padding:16px 18px 18px; }
    [data-testid="stSpinner"], [data-testid="stSpinner"] > div { background:transparent !important; }
    hr { border-color: #E6E9EF !important; }
    [data-testid="stDownloadButton"] button {
        background:#191970 !important; color:#FFFFFF !important;
        font-weight:900 !important; border-radius:10px !important;
    }
    </style>
    """, unsafe_allow_html=True)


# =================================================================
# [2] SVG 아바타
# =================================================================
CHRIS_SVG = '<svg width="72" height="72" viewBox="0 0 72 72" fill="none" xmlns="http://www.w3.org/2000/svg"><rect width="72" height="72" rx="16" fill="#D6E4F0"/><path d="M14 72 Q14 54 36 50 Q58 54 58 72Z" fill="#1B2A6B"/><path d="M30 50 L36 58 L42 50" fill="white" stroke="#1B2A6B" stroke-width="1.5"/><rect x="31" y="42" width="10" height="10" rx="3" fill="#F5C99A"/><ellipse cx="36" cy="30" rx="14" ry="15" fill="#F5C99A" stroke="#2D2D2D" stroke-width="1.8"/><path d="M22 26 Q22 12 36 11 Q50 12 50 26 Q46 18 36 18 Q26 18 22 26Z" fill="#2D2D2D"/><rect x="24" y="27" width="10" height="8" rx="3" fill="none" stroke="#2D2D2D" stroke-width="2"/><rect x="38" y="27" width="10" height="8" rx="3" fill="none" stroke="#2D2D2D" stroke-width="2"/><line x1="34" y1="31" x2="38" y2="31" stroke="#2D2D2D" stroke-width="2"/><circle cx="29" cy="31" r="2" fill="#2D2D2D"/><circle cx="43" cy="31" r="2" fill="#2D2D2D"/><path d="M30 40 Q36 43 42 40" stroke="#2D2D2D" stroke-width="1.8" fill="none" stroke-linecap="round"/></svg>'

SHIHO_SVG = '<svg width="72" height="72" viewBox="0 0 72 72" fill="none" xmlns="http://www.w3.org/2000/svg"><rect width="72" height="72" rx="16" fill="#EDE0FF"/><path d="M18 30 Q15 50 18 68 L28 68 Q24 48 24 30Z" fill="#3D2314"/><path d="M54 30 Q57 50 54 68 L44 68 Q48 48 48 30Z" fill="#3D2314"/><path d="M14 72 Q14 54 36 50 Q58 54 58 72Z" fill="#6B3FA0"/><rect x="31" y="42" width="10" height="10" rx="3" fill="#F5C99A"/><ellipse cx="36" cy="30" rx="14" ry="15" fill="#F5C99A" stroke="#2D2D2D" stroke-width="1.8"/><path d="M22 28 Q22 12 36 11 Q50 12 50 28 Q47 18 36 18 Q25 18 22 28Z" fill="#3D2314"/><ellipse cx="29" cy="29" rx="4" ry="4.5" fill="white" stroke="#2D2D2D" stroke-width="1.5"/><ellipse cx="43" cy="29" rx="4" ry="4.5" fill="white" stroke="#2D2D2D" stroke-width="1.5"/><circle cx="30" cy="30" r="2.5" fill="#3D2314"/><circle cx="44" cy="30" r="2.5" fill="#3D2314"/><ellipse cx="22" cy="33" rx="4" ry="2.5" fill="#FFB3C1" opacity="0.55"/><ellipse cx="50" cy="33" rx="4" ry="2.5" fill="#FFB3C1" opacity="0.55"/><path d="M29 40 Q36 45 43 40" stroke="#2D2D2D" stroke-width="1.8" fill="none" stroke-linecap="round"/><circle cx="22" cy="32" r="2.5" fill="#FFCB05" stroke="#2D2D2D" stroke-width="1"/><circle cx="50" cy="32" r="2.5" fill="#FFCB05" stroke="#2D2D2D" stroke-width="1"/></svg>'

MOON_SVG = '<svg width="72" height="72" viewBox="0 0 72 72" fill="none" xmlns="http://www.w3.org/2000/svg"><rect width="72" height="72" rx="16" fill="#DFF2E8"/><path d="M14 72 Q14 54 36 50 Q58 54 58 72Z" fill="#3D6B4F"/><path d="M30 50 Q36 54 42 50 L42 44 Q36 47 30 44Z" fill="#2D2D2D"/><rect x="31" y="42" width="10" height="10" rx="3" fill="#E8B88A"/><ellipse cx="36" cy="30" rx="14" ry="15" fill="#E8B88A" stroke="#2D2D2D" stroke-width="1.8"/><path d="M22 26 Q22 10 36 10 Q50 10 50 26 Q48 16 36 15 Q24 15 22 26Z" fill="#1A1A1A"/><path d="M24 29 Q29 27 34 29 Q29 33 24 29Z" fill="#1A1A1A"/><path d="M38 29 Q43 27 48 29 Q43 33 38 29Z" fill="#1A1A1A"/><circle cx="29" cy="29.5" r="1" fill="white"/><circle cx="43" cy="29.5" r="1" fill="white"/><path d="M29 42 Q36 44 43 42" stroke="#2D2D2D" stroke-width="2" fill="none" stroke-linecap="round"/></svg>'

AVATAR_MAP = {"CHRIS": CHRIS_SVG, "SHIHO": SHIHO_SVG, "MOON": MOON_SVG}


# =================================================================
# [3] 유틸리티
# =================================================================
def safe(text):
    return html.escape(str(text)) if text else ""

def parse_json(raw):
    if not raw:
        return None
    try:
        return json.loads(raw, strict=False)
    except Exception:
        try:
            cleaned = re.sub(r'```json\s*|```\s*', '', raw).strip()
            return json.loads(cleaned, strict=False)
        except Exception:
            return None

def get_client():
    api_key = st.secrets.get("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("ANTHROPIC_API_KEY가 secrets에 없습니다.")
        return None
    return anthropic.Anthropic(api_key=api_key)

def call_claude(client, prompt, max_tokens=8192, model=""):
    use_model = model or ANTHROPIC_MODEL_WRITE
    try:
        message = client.messages.create(
            model=use_model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        st.error(f"API 오류 ({use_model}): {e}")
        return None


# =================================================================
# [4] PDF 추출
# =================================================================
def extract_text(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        pages = [p.extract_text() for p in reader.pages if p.extract_text()]
        text = "\n".join(pages)
        if len(text) < 300:
            st.error("텍스트가 너무 짧습니다. 이미지 스캔 PDF는 분석 불가합니다.")
            return None
        return text[:80000]
    except Exception as e:
        st.error(f"PDF 추출 실패: {e}")
        return None


# =================================================================
# [5] 3단계 AI 실행 — prompt.py 연동
# =================================================================
def run_chris(text, client):
    """CHRIS — Analysis (PLAN 모델)"""
    prompt = build_analysis_prompt(text)
    raw = call_claude(client, prompt, model=ANTHROPIC_MODEL_PLAN)
    data = parse_json(raw)
    if data:
        s = data.get('scores', {})
        # 점수 정규화 (100점 방지)
        for k in ['structure', 'hero', 'concept', 'genre']:
            v = float(s.get(k, 0))
            if v > 10:
                s[k] = round(v / 10, 1)
        data['scores'] = s
        data['mark'] = {'final': round(
            s.get('structure', 0) * 0.3 + s.get('hero', 0) * 0.3 +
            s.get('concept', 0) * 0.2 + s.get('genre', 0) * 0.2, 1
        )}
    return data

def run_shiho(text, analysis, client):
    """SHIHO — Doctoring (PLAN 모델)"""
    prompt = build_doctoring_prompt(text, analysis)
    raw = call_claude(client, prompt, max_tokens=10000, model=ANTHROPIC_MODEL_PLAN)
    return parse_json(raw)

def run_moon(text, analysis, washing, client):
    """MOON — Rewrite (WRITE 모델 — Opus)"""
    prompt = build_rewrite_prompt(text, analysis, washing)
    raw = call_claude(client, prompt, max_tokens=16000, model=ANTHROPIC_MODEL_WRITE)
    result = parse_json(raw)
    if result and not result.get('rewriting', {}).get('scenes'):
        st.warning(f"scenes 파싱 실패. raw 앞 500자: {raw[:500] if raw else 'None'}")
    return result


# =================================================================
# [6] 리포트 렌더러 — Analysis
# =================================================================
def score_bar(val, color=C_NAVY):
    pct = min(int(float(val)) * 10, 100)
    return (f'<div style="display:flex;align-items:center;gap:8px;">'
            f'<div style="flex:1;background:#E6E9EF;border-radius:20px;height:8px;overflow:hidden;">'
            f'<div style="background:{color};width:{pct}%;height:100%;border-radius:20px;"></div></div>'
            f'<div style="font-size:0.82rem;font-weight:900;color:{color};min-width:28px;">{val}</div></div>')

def render_analysis(data):
    sc = data.get('scores', {})
    s_score, h_score = sc.get('structure', 0), sc.get('hero', 0)
    c_score, g_score = sc.get('concept', 0), sc.get('genre', 0)
    final = data.get('mark', {}).get('final', 0)
    verdict = data.get('verdict', {})
    verdict_color = {'추천': C_GREEN, '고려': C_YELLOW, '비추천': C_RED}.get(verdict.get('status', ''), C_NAVY)

    bar_s = score_bar(s_score, C_NAVY)
    bar_h = score_bar(h_score, C_NAVY)
    bar_c = score_bar(c_score, '#B8860B')
    bar_g = score_bar(g_score, C_GREEN)
    final_pct = min(int(float(final) * 10), 100)

    # 1. 종합 분석
    st.markdown(f"""
    <div class="report-card">
        <h3>1. 종합 분석 (Total Analysis)</h3>
        <div style="display:flex;align-items:center;gap:20px;margin-bottom:20px;background:#F0F2FF;border-radius:12px;padding:16px 20px;">
            <div style="text-align:center;min-width:70px;">
                <div style="font-size:3rem;font-weight:950;color:#FFCB05;line-height:1;">{final}</div>
                <div style="font-size:0.72rem;color:#191970;opacity:0.5;">/ 10.0</div>
            </div>
            <div style="width:1px;height:52px;background:#E0E4F0;"></div>
            <div style="flex:1;">
                <div style="display:inline-block;background:{verdict_color};color:#FFFFFF;padding:3px 14px;border-radius:20px;font-weight:900;font-size:0.82rem;margin-bottom:6px;">{safe(verdict.get('status',''))}</div>
                <div style="font-size:0.86rem;line-height:1.7;">{safe(verdict.get('rationale',''))}</div>
            </div>
        </div>
        <table style="width:100%;border-collapse:collapse;font-size:0.85rem;">
            <thead><tr style="background:#191970;">
                <th style="padding:8px 12px;text-align:left;color:#FFCB05 !important;font-size:0.72rem;width:22%;">AXIS</th>
                <th style="padding:8px 12px;text-align:left;color:#FFCB05 !important;font-size:0.72rem;width:18%;">가중치</th>
                <th style="padding:8px 12px;text-align:left;color:#FFCB05 !important;font-size:0.72rem;">평가 기준</th>
                <th style="padding:8px 12px;text-align:left;color:#FFCB05 !important;font-size:0.72rem;width:30%;">점수</th>
            </tr></thead>
            <tbody>
                <tr style="background:#F8F9FF;border-bottom:1px solid #E6E9EF;">
                    <td style="padding:10px 12px;font-weight:900;">① STRUCTURE</td><td style="padding:10px 12px;font-weight:700;">30%</td>
                    <td style="padding:10px 12px;font-size:0.82rem;">인과관계의 정밀도, 3막 구조</td><td style="padding:10px 12px;">{bar_s}</td>
                </tr>
                <tr style="background:#FFFFFF;border-bottom:1px solid #E6E9EF;">
                    <td style="padding:10px 12px;font-weight:900;">② HERO</td><td style="padding:10px 12px;font-weight:700;">30%</td>
                    <td style="padding:10px 12px;font-size:0.82rem;">Goal/Need/Strategy, 감정선</td><td style="padding:10px 12px;">{bar_h}</td>
                </tr>
                <tr style="background:#F8F9FF;border-bottom:1px solid #E6E9EF;">
                    <td style="padding:10px 12px;font-weight:900;">③ CONCEPT</td><td style="padding:10px 12px;font-weight:700;">20%</td>
                    <td style="padding:10px 12px;font-size:0.82rem;">하이컨셉, 독창성, 시장성</td><td style="padding:10px 12px;">{bar_c}</td>
                </tr>
                <tr style="background:#FFFFFF;border-bottom:1px solid #E6E9EF;">
                    <td style="padding:10px 12px;font-weight:900;">④ GENRE</td><td style="padding:10px 12px;font-weight:700;">20%</td>
                    <td style="padding:10px 12px;font-size:0.82rem;">장르 문법, 장르적 재미</td><td style="padding:10px 12px;">{bar_g}</td>
                </tr>
                <tr style="background:#EEF0FA;">
                    <td colspan="2" style="padding:10px 12px;font-weight:900;font-size:0.9rem;">FINAL</td>
                    <td style="padding:10px 12px;font-size:0.78rem;opacity:0.6;">0.3S + 0.3H + 0.2C + 0.2G</td>
                    <td style="padding:10px 12px;"><div style="display:flex;align-items:center;gap:8px;">
                        <div style="flex:1;background:#C5CBE8;border-radius:20px;height:8px;overflow:hidden;">
                            <div style="background:#FFCB05;width:{final_pct}%;height:100%;border-radius:20px;"></div></div>
                        <div style="font-size:0.95rem;font-weight:950;color:#FFCB05;">{final}</div></div></td>
                </tr>
            </tbody>
        </table>
    </div>""", unsafe_allow_html=True)

    # 2. 로그라인
    log = data.get('logline', {})
    st.markdown(f"""
    <div class="report-card">
        <h3>2. 로그라인 분석 (Logline Pack)</h3>
        <div style="padding:14px;border:1px solid #E6E9EF;border-radius:8px;margin-bottom:12px;">
            <div style="font-size:0.7rem;font-weight:700;letter-spacing:0.12em;margin-bottom:6px;opacity:0.6;">ORIGINAL</div>
            <div style="line-height:1.7;">{safe(log.get('original', ''))}</div>
        </div>
        <div style="padding:14px;border:2px solid #FFCB05;border-radius:8px;background:#FFFBE6;">
            <div style="font-size:0.7rem;font-weight:700;letter-spacing:0.12em;margin-bottom:6px;color:#B8860B;">WASHED</div>
            <div style="font-weight:700;font-size:1.05rem;line-height:1.7;">{safe(log.get('washed', ''))}</div>
        </div>
    </div>""", unsafe_allow_html=True)

    # 3. 줄거리
    st.markdown(f'<div class="report-card"><h3>3. 줄거리 (Synopsis)</h3><div style="line-height:1.9;">{safe(data.get("synopsis", ""))}</div></div>', unsafe_allow_html=True)

    # 4. 장단점
    pc = data.get('pros_cons', {})
    pros_html = "".join([f"<li style='margin-bottom:7px;line-height:1.6;'>{safe(p)}</li>" for p in pc.get('pros', [])])
    cons_html = "".join([f"<li style='margin-bottom:7px;line-height:1.6;'>{safe(c)}</li>" for c in pc.get('cons', [])])
    st.markdown(f"""
    <div class="report-card">
        <h3>4. 장점 및 보완점 (Pros & Cons)</h3>
        <div style="display:flex;gap:14px;">
            <div style="flex:1;background:#EDFAF3;border-left:3px solid #2EC484;padding:16px;border-radius:8px;">
                <div style="color:#1A7A50;font-weight:800;font-size:0.75rem;margin-bottom:10px;">PROS</div>
                <ul style="margin:0;padding-left:16px;">{pros_html}</ul>
            </div>
            <div style="flex:1;background:#FFF3EE;border-left:3px solid #FF6432;padding:16px;border-radius:8px;">
                <div style="color:#CC3300;font-weight:800;font-size:0.75rem;margin-bottom:10px;">CONS</div>
                <ul style="margin:0;padding-left:16px;">{cons_html}</ul>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)
    prescription = safe(pc.get('prescription', ''))
    if prescription:
        st.markdown(f'<div style="background:#FFFBE6;border-left:4px solid #FFCB05;padding:14px 16px;border-radius:8px;margin-top:-8px;margin-bottom:16px;"><div style="font-size:0.75rem;font-weight:800;color:#B8860B;margin-bottom:6px;">핵심 처방 (Key Prescription)</div><div style="font-size:0.9rem;line-height:1.8;font-weight:600;">{prescription}</div></div>', unsafe_allow_html=True)

    # 5. 서사동력
    drive = data.get('drive', {})
    ev = drive.get('evaluation', {})
    st.markdown(f"""
    <div class="report-card">
        <h3>5. 서사 동력 (Narrative Drive)</h3>
        <div style="display:flex;gap:10px;margin-bottom:14px;">
            <div style="flex:1;background:#FFFBE6;padding:14px;border-radius:10px;text-align:center;border:1px solid #FFE066;">
                <div style="font-size:0.72rem;color:#B8860B;font-weight:700;margin-bottom:7px;">Goal</div>
                <div style="font-size:0.87rem;line-height:1.5;">{safe(drive.get('goal',''))}</div>
            </div>
            <div style="flex:1;background:#FFFBE6;padding:14px;border-radius:10px;text-align:center;border:1px solid #FFE066;">
                <div style="font-size:0.72rem;color:#B8860B;font-weight:700;margin-bottom:7px;">Lack</div>
                <div style="font-size:0.87rem;line-height:1.5;">{safe(drive.get('lack',''))}</div>
            </div>
            <div style="flex:1;background:#FFFBE6;padding:14px;border-radius:10px;text-align:center;border:1px solid #FFE066;">
                <div style="font-size:0.72rem;color:#B8860B;font-weight:700;margin-bottom:7px;">Strategy</div>
                <div style="font-size:0.87rem;line-height:1.5;">{safe(drive.get('strategy',''))}</div>
            </div>
        </div>
        <div style="background:#EEF0FA;padding:14px;border-radius:8px;border:1px solid #C5CBE8;">
            <p style="margin:4px 0;font-size:0.88rem;"><strong>목적 명확성</strong> {safe(ev.get('clarity',''))}</p>
            <p style="margin:4px 0;font-size:0.88rem;"><strong>발생요인 확실성</strong> {safe(ev.get('urgency',''))}</p>
            <p style="margin:4px 0;font-size:0.88rem;"><strong>해결전략 창의성</strong> {safe(ev.get('consistency',''))}</p>
            <p style="margin:10px 0 0;font-size:0.88rem;line-height:1.7;border-top:1px solid #C5CBE8;padding-top:10px;">{safe(ev.get('overall_diagnosis',''))}</p>
        </div>
    </div>""", unsafe_allow_html=True)

    # 6. 15-Beat Sheet
    beats = data.get('beats', {})
    circles = {i: c for i, c in enumerate(['①','②','③','④','⑤','⑥','⑦','⑧','⑨','⑩','⑪','⑫','⑬','⑭','⑮'], 1)}
    rows = ""
    for idx, (k, v) in enumerate(sorted(beats.items()), 1):
        name = re.sub(r'^[\d\.\-\_\s]+', '', str(k)).strip()
        bg = "#F8F9FF" if idx % 2 == 0 else "#FFFFFF"
        rows += (f'<tr style="background:{bg};border-bottom:1px solid #E6E9EF;">'
                 f'<td style="padding:9px 14px;font-weight:700;width:26%;font-size:0.85rem;">{circles.get(idx,"")} {safe(name)}</td>'
                 f'<td style="padding:9px 14px;line-height:1.6;font-size:0.86rem;">{safe(v)}</td></tr>')
    st.markdown(f'<div class="report-card"><h3>6. 구성 및 플롯 (15-Beat Sheet)</h3><table style="width:100%;border-collapse:collapse;"><thead><tr style="background:#191970;"><th style="padding:9px 14px;text-align:left;font-size:0.75rem;color:#FFCB05 !important;width:26%;">BEAT</th><th style="padding:9px 14px;text-align:left;font-size:0.75rem;color:#FFCB05 !important;">DESCRIPTION</th></tr></thead><tbody>{rows}</tbody></table></div>', unsafe_allow_html=True)

    # 7. 시각화
    st.markdown('<div class="report-card"><h3>7. 시각화 (Visualization)</h3></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        arc = data.get('tension_data', [])
        nums = [float(v) for v in arc if str(v).replace('.','').replace('-','').isdigit()]
        if nums:
            fig = px.line(y=nums, template="plotly_white", title="긴장도 곡선")
            fig.update_traces(line_color=C_NAVY, line_width=2.5, mode='lines+markers',
                              marker=dict(size=6, color=C_YELLOW, line=dict(color=C_NAVY, width=1)))
            fig.update_layout(height=260, margin=dict(l=10,r=10,t=36,b=10),
                              paper_bgcolor=C_WHITE, plot_bgcolor=C_WHITE,
                              yaxis=dict(range=[0,11], gridcolor=C_BORDER), title_font_size=13)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    with col2:
        chars = data.get('characters', {})
        names, ratios = chars.get('names', []), [float(r) for r in chars.get('ratios', []) if str(r).replace('.','').isdigit()]
        if names and ratios:
            fig2 = px.pie(values=ratios[:len(names)], names=names[:len(ratios)], hole=0.45, title="인물 비중",
                          color_discrete_sequence=[C_NAVY, C_YELLOW, C_GREEN, C_RED, '#94A3B8'])
            fig2.update_layout(height=260, margin=dict(l=10,r=10,t=36,b=10), paper_bgcolor=C_WHITE, title_font_size=13)
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

    # 8. 장르 분석 — 강화: genre_fun, must_have_check, hook_punch
    gc = data.get('genre_compliance', {})
    genre_key = gc.get('genre_key', '')
    compliance = gc.get('compliance_score', 0)
    bar_color = C_GREEN if compliance >= 7 else (C_YELLOW if compliance >= 4 else C_RED)
    genre_fun_alive = gc.get('genre_fun_alive', False)
    fun_badge_color = C_GREEN if genre_fun_alive else C_RED
    fun_badge_text = "장르적 재미 살아있음" if genre_fun_alive else "장르적 재미 약함"

    st.markdown(f"""
    <div class="report-card">
        <h3>8. 장르 분석 (Genre Compliance)</h3>
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;">
            <div style="font-size:1.5rem;font-weight:900;">{safe(gc.get('genre_key', genre_key))}</div>
            <div style="flex:1;background:#E6E9EF;border-radius:20px;height:10px;overflow:hidden;">
                <div style="background:{bar_color};width:{compliance*10}%;height:100%;border-radius:20px;"></div></div>
            <div style="font-size:1.1rem;font-weight:900;color:{bar_color};">{compliance}/10</div>
            <span style="background:{fun_badge_color};color:#FFFFFF;padding:4px 12px;border-radius:20px;font-size:0.75rem;font-weight:800;">{fun_badge_text}</span>
        </div>
        <div style="background:#EEF0FA;padding:14px;border-radius:8px;line-height:1.8;margin-bottom:12px;">{safe(gc.get('genre_fun_diagnosis',''))}</div>
    </div>""", unsafe_allow_html=True)

    # Must-have 체크
    must_checks = gc.get('must_have_check', [])
    if must_checks:
        for mc in must_checks:
            status = mc.get('status', '')
            s_color = C_GREEN if status == '충족' else (C_YELLOW if status == '약함' else C_RED)
            s_icon = '✓' if status == '충족' else ('△' if status == '약함' else '✗')
            st.markdown(f"""
            <div style="background:#FFFFFF;border:1px solid #E6E9EF;border-radius:8px;padding:10px 14px;margin-bottom:6px;display:flex;align-items:center;gap:10px;">
                <span style="background:{s_color};color:#FFFFFF;width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:0.75rem;flex-shrink:0;">{s_icon}</span>
                <span style="font-weight:700;font-size:0.85rem;">{safe(mc.get('item',''))}</span>
                <span style="font-size:0.8rem;opacity:0.7;margin-left:auto;">{safe(mc.get('evidence',''))}</span>
            </div>""", unsafe_allow_html=True)

    # Hook/Punch 체크
    hp = gc.get('hook_punch_check', {})
    if hp:
        st.markdown(f"""
        <div style="display:flex;gap:10px;margin-top:10px;">
            <div style="flex:1;background:{'#EDFAF3' if hp.get('hook_present') else '#FFF3EE'};border-left:3px solid {'#2EC484' if hp.get('hook_present') else '#FF6432'};padding:12px;border-radius:8px;">
                <div style="font-size:0.72rem;font-weight:800;color:{'#1A7A50' if hp.get('hook_present') else '#CC3300'};margin-bottom:4px;">Hook {'✓' if hp.get('hook_present') else '✗'}</div>
                <div style="font-size:0.85rem;line-height:1.6;">{safe(hp.get('hook_note',''))}</div>
            </div>
            <div style="flex:1;background:{'#EDFAF3' if hp.get('punch_present') else '#FFF3EE'};border-left:3px solid {'#2EC484' if hp.get('punch_present') else '#FF6432'};padding:12px;border-radius:8px;">
                <div style="font-size:0.72rem;font-weight:800;color:{'#1A7A50' if hp.get('punch_present') else '#CC3300'};margin-bottom:4px;">Punch {'✓' if hp.get('punch_present') else '✗'}</div>
                <div style="font-size:0.85rem;line-height:1.6;">{safe(hp.get('punch_note',''))}</div>
            </div>
        </div>""", unsafe_allow_html=True)

    # 실패 패턴
    fails = gc.get('fail_patterns_found', [])
    if fails:
        fails_html = "".join([f"<span style='background:#FFF3EE;color:#CC3300;border:1px solid #FF6432;padding:3px 10px;border-radius:20px;font-size:0.75rem;font-weight:700;margin-right:6px;margin-bottom:6px;display:inline-block;'>✗ {safe(f)}</span>" for f in fails])
        st.markdown(f'<div style="margin-top:10px;"><strong style="font-size:0.78rem;color:#CC3300;display:block;margin-bottom:6px;">발견된 장르 실패 패턴</strong>{fails_html}</div>', unsafe_allow_html=True)


# =================================================================
# [7] 리포트 렌더러 — Washing
# =================================================================
def render_washing(data):
    # 9-A. 시퀀스 워싱
    st.markdown('<div class="report-card"><h3>9-A. 시퀀스 워싱 (Washing Table)</h3></div>', unsafe_allow_html=True)
    for row in data.get('washing_table', []):
        seq = safe(row.get('seq', ''))
        label = safe(row.get('label', ''))
        problem_types = row.get('problem_types', [])
        pt_html = " ".join([f"<span style='background:#FFFBE6;color:#B8860B;border:1px solid #FFE066;padding:1px 8px;border-radius:12px;font-size:0.68rem;font-weight:700;'>{safe(p)}</span>" for p in problem_types])
        genre_fix = row.get('genre_fix', '')
        preserve_note = row.get('preserve_note', '')
        st.markdown(f"""
        <div style="background:#FFFFFF;border:1px solid #E6E9EF;border-radius:10px;padding:16px;margin-bottom:12px;">
            <div style="margin-bottom:10px;">
                <span style="background:#191970;color:#FFFFFF !important;padding:2px 10px;border-radius:4px;font-weight:900;font-size:0.72rem;">{seq}</span>
                <span style="font-weight:700;margin-left:10px;">{label}</span>
                <span style="margin-left:10px;">{pt_html}</span>
            </div>
            <div style="display:flex;gap:12px;">
                <div style="flex:1;background:#FFF5F5;padding:12px;border-radius:8px;border-left:3px solid #D32F2F;">
                    <div style="color:#D32F2F;font-size:0.72rem;font-weight:800;margin-bottom:5px;">진단</div>
                    <div style="font-size:0.88rem;line-height:1.6;">{safe(row.get('diagnosis',''))}</div>
                </div>
                <div style="flex:1.2;background:#EEF0FA;padding:12px;border-radius:8px;border-left:3px solid #191970;">
                    <div style="font-size:0.72rem;font-weight:800;margin-bottom:5px;">처방</div>
                    <div style="font-size:0.88rem;line-height:1.6;">{safe(row.get('prescription',''))}</div>
                </div>
            </div>
            <div style="background:#FFF8E1;padding:8px 12px;border-radius:6px;margin-top:8px;font-size:0.82rem;line-height:1.5;">
                <strong style="color:#B8860B;">Risk:</strong> {safe(row.get('risk',''))}
            </div>
            {"<div style='background:#F0F7FF;padding:8px 12px;border-radius:6px;margin-top:6px;font-size:0.82rem;line-height:1.5;border-left:3px solid #4A90D9;'><strong style='color:#2A5DB0;'>보존:</strong> " + safe(preserve_note) + "</div>" if preserve_note else ""}
            {"<div style='background:#EDFAF3;padding:8px 12px;border-radius:6px;margin-top:6px;font-size:0.82rem;line-height:1.5;'><strong style='color:#1A7A50;'>장르 복구:</strong> " + safe(genre_fix) + "</div>" if genre_fix else ""}
        </div>""", unsafe_allow_html=True)

    # 9-B. 대사 워싱
    da = data.get('dialogue_analysis', {})
    if da:
        def norm(v):
            v = float(v or 0)
            return round(v / 10, 1) if v > 10 else v

        score = norm(da.get('overall_score', 0))
        bar_color = C_GREEN if score >= 7 else (C_YELLOW if score >= 4 else C_RED)
        ax = da.get('axis_scores', {})
        cv = norm(ax.get('character_voice', 0))
        st_ = norm(ax.get('subtext', 0))
        ad = norm(ax.get('action_driven', 0))

        def mini_bar(val, color):
            pct = min(int(float(val) * 10), 100)
            return (f'<div style="display:flex;align-items:center;gap:6px;">'
                    f'<div style="flex:1;background:#E6E9EF;border-radius:10px;height:6px;overflow:hidden;">'
                    f'<div style="background:{color};width:{pct}%;height:100%;border-radius:10px;"></div></div>'
                    f'<span style="font-size:0.78rem;font-weight:900;color:{color};">{val}</span></div>')

        st.markdown(f"""
        <div class="report-card">
            <h3>9-B. 대사 워싱 (Dialogue Washing)</h3>
            <table style="width:100%;border-collapse:collapse;margin-bottom:10px;">
                <thead><tr style="background:#191970;">
                    <th style="padding:7px 12px;text-align:left;color:#FFCB05 !important;font-size:0.7rem;">축</th>
                    <th style="padding:7px 12px;text-align:left;color:#FFCB05 !important;font-size:0.7rem;width:35%;">점수</th>
                </tr></thead>
                <tbody>
                    <tr style="background:#F8F9FF;border-bottom:1px solid #E6E9EF;">
                        <td style="padding:8px 12px;font-weight:800;font-size:0.82rem;">① 캐릭터 적합성</td>
                        <td style="padding:8px 12px;">{mini_bar(cv, C_NAVY)}</td>
                    </tr>
                    <tr style="background:#FFFFFF;border-bottom:1px solid #E6E9EF;">
                        <td style="padding:8px 12px;font-weight:800;font-size:0.82rem;">② 서브텍스트</td>
                        <td style="padding:8px 12px;">{mini_bar(st_, '#6B3FA0')}</td>
                    </tr>
                    <tr style="background:#F8F9FF;border-bottom:1px solid #E6E9EF;">
                        <td style="padding:8px 12px;font-weight:800;font-size:0.82rem;">③ 행동 구동</td>
                        <td style="padding:8px 12px;">{mini_bar(ad, C_GREEN)}</td>
                    </tr>
                    <tr style="background:#EEF0FA;">
                        <td style="padding:8px 12px;font-weight:900;font-size:0.88rem;">종합</td>
                        <td style="padding:8px 12px;">{mini_bar(score, bar_color)}</td>
                    </tr>
                </tbody>
            </table>
            <div style="background:#EEF0FA;padding:14px;border-radius:8px;line-height:1.8;">{safe(da.get('overall_comment',''))}</div>
        </div>""", unsafe_allow_html=True)

        # Issues Before/After
        issues = da.get('issues', [])
        for issue in issues:
            st.markdown(f"""
            <div style="background:#FFFFFF;border:1px solid #E6E9EF;border-radius:10px;padding:16px;margin-bottom:12px;">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
                    <span style="background:#FF6432;color:#FFFFFF;padding:2px 10px;border-radius:4px;font-weight:900;font-size:0.72rem;">{safe(issue.get('type',''))}</span>
                    <span style="font-size:0.83rem;color:#555;">{safe(issue.get('description',''))}</span>
                </div>
                <div style="display:flex;gap:10px;margin-bottom:10px;">
                    <div style="flex:1;background:#FFF5F5;padding:11px;border-radius:8px;border-left:3px solid #FF6432;">
                        <div style="font-size:0.68rem;font-weight:800;color:#CC3300;margin-bottom:5px;">BEFORE</div>
                        <div style="font-size:0.88rem;line-height:1.6;font-family:'Courier New',monospace;">{safe(issue.get('example_bad',''))}</div>
                    </div>
                    <div style="flex:1;background:#EDFAF3;padding:11px;border-radius:8px;border-left:3px solid #2EC484;">
                        <div style="font-size:0.68rem;font-weight:800;color:#1A7A50;margin-bottom:5px;">AFTER</div>
                        <div style="font-size:0.88rem;line-height:1.6;font-family:'Courier New',monospace;">{safe(issue.get('example_good',''))}</div>
                    </div>
                </div>
                <div style="background:#FFFBE6;padding:10px;border-radius:6px;border-left:3px solid #FFCB05;">
                    <div style="font-size:0.68rem;font-weight:800;color:#B8860B;margin-bottom:4px;">Moon 리라이팅 지시</div>
                    <div style="font-size:0.85rem;">{safe(issue.get('rewrite_note',''))}</div>
                </div>
            </div>""", unsafe_allow_html=True)

    # 9-C. 장르 재미 복구 제안 (신규 섹션)
    gfr = data.get('genre_fun_recovery', {})
    if gfr:
        weak_zones = gfr.get('weak_zones', [])
        if weak_zones:
            st.markdown('<div class="report-card"><h3>9-C. 장르 재미 복구 (Genre Fun Recovery)</h3>', unsafe_allow_html=True)
            st.markdown(f'<div style="background:#FFFBE6;padding:12px;border-radius:8px;margin-bottom:12px;line-height:1.7;border-left:3px solid #FFCB05;">{safe(gfr.get("overall_direction",""))}</div>', unsafe_allow_html=True)
            for wz in weak_zones:
                st.markdown(f"""
                <div style="background:#FFFFFF;border:1px solid #E6E9EF;border-radius:8px;padding:14px;margin-bottom:8px;">
                    <div style="font-weight:800;margin-bottom:8px;">{safe(wz.get('seq_ref',''))}: {safe(wz.get('what_is_missing',''))}</div>
                    <div style="display:flex;gap:10px;">
                        <div style="flex:1;background:#F0F2FF;padding:10px;border-radius:6px;">
                            <div style="font-size:0.68rem;font-weight:800;color:#191970;margin-bottom:3px;">Hook 제안</div>
                            <div style="font-size:0.85rem;line-height:1.5;">{safe(wz.get('hook_suggestion',''))}</div>
                        </div>
                        <div style="flex:1;background:#F0F2FF;padding:10px;border-radius:6px;">
                            <div style="font-size:0.68rem;font-weight:800;color:#191970;margin-bottom:3px;">Punch 제안</div>
                            <div style="font-size:0.85rem;line-height:1.5;">{safe(wz.get('punch_suggestion',''))}</div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # 10. 각색 제안
    suggestions = data.get('suggestions', [])
    st.markdown('<div class="report-card"><h3>10. 각색 제안 (Action Plan)</h3>', unsafe_allow_html=True)
    for i, s in enumerate(suggestions, 1):
        clean = re.sub(r'^[\d\.\s]+', '', str(s)).strip()
        st.markdown(f"""
        <div style="background:#F8F9FF;border:1px solid #E6E9EF;border-radius:8px;padding:12px;display:flex;gap:10px;align-items:flex-start;margin-bottom:8px;">
            <div style="background:#191970;color:#FFFFFF !important;border-radius:5px;padding:2px 8px;font-weight:900;font-size:0.68rem;white-space:nowrap;flex-shrink:0;">STEP {i:02d}</div>
            <div style="font-size:0.88rem;line-height:1.5;">{safe(clean)}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# =================================================================
# [8] 리포트 렌더러 — Rewriting (강화: Hook/Punch, linked_diagnosis)
# =================================================================
def render_rewriting(data):
    rewrite = data.get('rewriting', {})
    scenes = rewrite.get('scenes', [])
    revised_count = sum(1 for s in scenes if s.get('type') == '수정씬')
    added_count = sum(1 for s in scenes if s.get('type') == '추가씬')

    st.markdown(f"""
    <div class="report-card">
        <h3>11. 각색 원고 (Rewrite Scenes)</h3>
        <div style="background:#FFFBE6;padding:14px;border-radius:8px;border-left:3px solid #FFCB05;margin-bottom:16px;line-height:1.8;">
            <strong style="font-size:0.75rem;display:block;margin-bottom:5px;">각색 전략</strong>
            <span>{safe(rewrite.get('target_reason', ''))}</span>
        </div>
        <div style="display:flex;gap:10px;margin-bottom:4px;">
            <span style="background:#191970;color:#FFFFFF !important;padding:4px 14px;border-radius:20px;font-size:0.78rem;font-weight:800;">총 {len(scenes)}개 씬</span>
            <span style="background:#2EC484;color:#FFFFFF;padding:4px 14px;border-radius:20px;font-size:0.78rem;font-weight:800;">수정씬 {revised_count}</span>
            <span style="background:#FF6432;color:#FFFFFF;padding:4px 14px;border-radius:20px;font-size:0.78rem;font-weight:800;">추가씬 {added_count}</span>
        </div>
    </div>""", unsafe_allow_html=True)

    for i, sc in enumerate(scenes):
        scene_type = sc.get('type', '수정씬')
        is_revised = scene_type == '수정씬'
        badge_color = C_GREEN if is_revised else C_RED
        badge_icon = '✏️' if is_revised else '✨'
        scene_no = safe(sc.get('scene_no', f'Scene {i+1}'))
        content = sc.get('content', '')
        original = sc.get('original', '')
        insert_between = sc.get('insert_between', '')
        linked = sc.get('linked_diagnosis', '')
        hook_desc = sc.get('hook', '')
        punch_desc = sc.get('punch', '')

        st.markdown(f"""
        <div style="background:#FFFFFF;border:2px solid {badge_color};border-radius:12px;padding:16px 20px;margin-bottom:8px;">
            <div style="font-size:0.88rem;font-weight:900;margin-bottom:6px;">{badge_icon} {scene_no} [{scene_type}]</div>
        """, unsafe_allow_html=True)

        # 진단 연결 (신규)
        if linked:
            st.markdown(f'<div style="background:#F0F2FF;border-left:3px solid #191970;padding:8px 14px;border-radius:6px;margin-bottom:8px;font-size:0.82rem;"><strong>진단 연결:</strong> {safe(linked)}</div>', unsafe_allow_html=True)

        # Hook/Punch 표시 (신규)
        if hook_desc or punch_desc:
            st.markdown(f"""
            <div style="display:flex;gap:8px;margin-bottom:8px;">
                <div style="flex:1;background:#FFFBE6;padding:8px 10px;border-radius:6px;font-size:0.78rem;"><strong style="color:#B8860B;">Hook:</strong> {safe(hook_desc)}</div>
                <div style="flex:1;background:#FFFBE6;padding:8px 10px;border-radius:6px;font-size:0.78rem;"><strong style="color:#B8860B;">Punch:</strong> {safe(punch_desc)}</div>
            </div>""", unsafe_allow_html=True)

        if not is_revised and insert_between:
            st.markdown(f'<div style="background:#EEF0FA;border-left:3px solid #191970;padding:8px 14px;border-radius:6px;margin-bottom:8px;font-size:0.82rem;">삽입 위치: {safe(insert_between)}</div>', unsafe_allow_html=True)

        if original:
            st.markdown(f'<div style="background:#F5F5F5;border-left:3px solid #AAAAAA;padding:10px 14px;border-radius:8px;margin-bottom:8px;"><div style="font-size:0.68rem;font-weight:800;color:#888;margin-bottom:4px;">BEFORE</div><div style="font-size:0.84rem;color:#555;line-height:1.7;">{safe(original)}</div></div>', unsafe_allow_html=True)

        # 각본 렌더링
        if content:
            lines = content.replace('\\n', '\n').split('\n')
            formatted = ""
            for line in lines:
                ls = line.strip()
                if not ls:
                    formatted += "<div style='height:8px;'></div>"
                elif ls.startswith('INT.') or ls.startswith('EXT.'):
                    formatted += f'<div style="font-weight:900;font-size:0.9rem;letter-spacing:0.05em;margin:10px 0 4px;">{safe(ls)}</div>'
                elif ':' in ls and len(ls.split(':')[0]) < 20:
                    parts = ls.split(':', 1)
                    formatted += f'<div style="margin:6px 0 3px;padding-left:12px;"><span style="font-weight:900;font-size:0.86rem;">{safe(parts[0])}:</span> <span style="font-size:0.86rem;line-height:1.7;">{safe(parts[1].strip())}</span></div>'
                else:
                    formatted += f'<div style="color:#444;font-size:0.85rem;line-height:1.75;margin:2px 0;">{safe(ls)}</div>'
            st.markdown(f'<div style="background:#FAFAFA;border:1px solid #E6E9EF;border-radius:8px;padding:16px 20px;font-family:\'Courier Prime\',\'Courier New\',monospace;">{formatted}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)


# =================================================================
# [9] DOCX 생성 — python-docx 통합 (gen_docx.js 제거)
# =================================================================
def create_docx(item):
    """python-docx로 보고서 생성 — Denim Look 스타일"""
    doc = Document()

    # 기본 스타일 설정
    style = doc.styles['Normal']
    style.font.name = 'Pretendard'
    style.font.size = Pt(10)
    style.font.color.rgb = RGBColor(0x19, 0x19, 0x70)

    def add_section_header(text, level=1):
        """노란 하이라이트 섹션 헤더"""
        p = doc.add_heading(text, level)
        for run in p.runs:
            run.font.color.rgb = RGBColor(0x19, 0x19, 0x70)
        return p

    def add_body(text):
        p = doc.add_paragraph(str(text))
        p.paragraph_format.line_spacing = 1.5
        return p

    def add_table_row(table, cells_data, bold=False, header=False):
        row = table.add_row()
        for i, (text, width) in enumerate(cells_data):
            cell = row.cells[i]
            cell.text = str(text)
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(9)
                    if header:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(0xFF, 0xCB, 0x05)
                    elif bold:
                        run.font.bold = True
            if header:
                shading_elm = cell._element.get_or_add_tcPr()
                shading = qn('w:shd')
                from lxml import etree
                shd = etree.SubElement(shading_elm, shading)
                shd.set(qn('w:fill'), '191970')
                shd.set(qn('w:val'), 'clear')

    # ── 표지 ──
    doc.add_paragraph()
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("BLUE JEANS PICTURES")
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(0xFF, 0xCB, 0x05)
    run.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("시나리오 검토 보고서")
    run.font.size = Pt(28)
    run.font.color.rgb = RGBColor(0x19, 0x19, 0x70)
    run.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(item.get('title', ''))
    run.font.size = Pt(16)
    run.font.color.rgb = RGBColor(0x19, 0x19, 0x70)

    # Verdict + Score
    sc = item.get('scores', {})
    final = item.get('mark', {}).get('final', 0)
    verdict = item.get('verdict', {})
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"\nFinal Score: {final} / 10.0  |  {verdict.get('status', '')}")
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0xFF, 0xCB, 0x05)
    run.bold = True

    doc.add_page_break()

    # ── 1. 종합 분석 ──
    add_section_header("1. 종합 분석 (Total Analysis)")
    add_body(f"Final Score: {final} / 10.0")
    add_body(f"Verdict: {verdict.get('status', '')} — {verdict.get('rationale', '')}")
    add_body(f"STRUCTURE: {sc.get('structure',0)} | HERO: {sc.get('hero',0)} | CONCEPT: {sc.get('concept',0)} | GENRE: {sc.get('genre',0)}")

    # ── 2. 로그라인 ──
    add_section_header("2. 로그라인 분석 (Logline Pack)")
    log = item.get('logline', {})
    add_body(f"Original: {log.get('original', '')}")
    add_body(f"Washed: {log.get('washed', '')}")

    # ── 3. 줄거리 ──
    add_section_header("3. 줄거리 (Synopsis)")
    add_body(item.get('synopsis', ''))

    # ── 4. 장단점 ──
    add_section_header("4. 장점 및 보완점 (Pros & Cons)")
    pc = item.get('pros_cons', {})
    for p_item in pc.get('pros', []):
        add_body(f"[+] {p_item}")
    for c_item in pc.get('cons', []):
        add_body(f"[-] {c_item}")
    if pc.get('prescription'):
        add_body(f"처방: {pc.get('prescription', '')}")

    # ── 5. 서사동력 ──
    add_section_header("5. 서사 동력 (Narrative Drive)")
    drive = item.get('drive', {})
    add_body(f"Goal: {drive.get('goal', '')}")
    add_body(f"Lack: {drive.get('lack', '')}")
    add_body(f"Strategy: {drive.get('strategy', '')}")
    ev = drive.get('evaluation', {})
    if ev.get('overall_diagnosis'):
        add_body(f"총평: {ev.get('overall_diagnosis', '')}")

    # ── 6. 15-Beat Sheet ──
    add_section_header("6. 구성 및 플롯 (15-Beat Sheet)")
    beats = item.get('beats', {})
    for k, v in sorted(beats.items()):
        name = re.sub(r'^[\d\.\-\_\s]+', '', str(k)).strip()
        add_body(f"{name}: {v}")

    doc.add_page_break()

    # ── 7. 장르 분석 ──
    add_section_header("7. 장르 분석 (Genre Compliance)")
    gc = item.get('genre_compliance', {})
    add_body(f"장르: {gc.get('genre_key', '')} | 적합도: {gc.get('compliance_score', 0)}/10")
    if gc.get('genre_fun_diagnosis'):
        add_body(f"장르적 재미: {gc.get('genre_fun_diagnosis', '')}")
    for mc in gc.get('must_have_check', []):
        add_body(f"  [{mc.get('status','')}] {mc.get('item','')} — {mc.get('evidence','')}")
    for f in gc.get('fail_patterns_found', []):
        add_body(f"  [실패 패턴] {f}")

    # ── 8. 시퀀스 워싱 ──
    add_section_header("8. 시퀀스 워싱 (Washing Table)")
    for row in item.get('washing_table', []):
        add_body(f"[{row.get('seq','')}] {row.get('label','')}")
        add_body(f"  문제: {', '.join(row.get('problem_types', []))}")
        add_body(f"  진단: {row.get('diagnosis','')}")
        add_body(f"  처방: {row.get('prescription','')}")
        add_body(f"  Risk: {row.get('risk','')}")
        if row.get('genre_fix'):
            add_body(f"  장르 복구: {row.get('genre_fix','')}")

    # ── 9. 대사 워싱 ──
    da = item.get('dialogue_analysis', {})
    if da:
        add_section_header("9. 대사 워싱 (Dialogue Washing)")
        add_body(f"종합: {da.get('overall_score', 0)}/10 — {da.get('overall_comment', '')}")
        for issue in da.get('issues', []):
            add_body(f"  [{issue.get('type','')}] {issue.get('description','')}")
            add_body(f"    BEFORE: {issue.get('example_bad','')}")
            add_body(f"    AFTER: {issue.get('example_good','')}")

    doc.add_page_break()

    # ── 10. 각색 제안 ──
    add_section_header("10. 각색 제안 (Action Plan)")
    for i, s in enumerate(item.get('suggestions', []), 1):
        clean_s = re.sub(r'^[\d\.\s]+', '', str(s)).strip()
        add_body(f"STEP {i:02d}  {clean_s}")

    # ── 11. 각색 원고 ──
    doc.add_page_break()
    add_section_header("11. 각색 원고 (Rewrite Scenes)")
    rw = item.get('rewriting', {})
    if rw.get('target_reason'):
        add_body(f"각색 전략: {rw.get('target_reason','')}")
    for sc_item in rw.get('scenes', []):
        is_r = sc_item.get('type') == '수정씬'
        p = doc.add_heading(f"{sc_item.get('scene_no','')}  [{'수정씬' if is_r else '추가씬'}]", level=2)
        for run in p.runs:
            run.font.color.rgb = RGBColor(0x19, 0x19, 0x70)
        if sc_item.get('linked_diagnosis'):
            add_body(f"진단 연결: {sc_item.get('linked_diagnosis','')}")
        if sc_item.get('hook'):
            add_body(f"Hook: {sc_item.get('hook','')} | Punch: {sc_item.get('punch','')}")
        if sc_item.get('original'):
            add_body(f"[BEFORE] {sc_item.get('original','')}")
        content = sc_item.get('content', '').replace('\\n', '\n')
        for line in content.split('\n'):
            ls = line.strip()
            if ls:
                p = doc.add_paragraph(ls)
                if ls.startswith('INT.') or ls.startswith('EXT.'):
                    for run in p.runs:
                        run.bold = True
                        run.font.name = 'Courier New'
                        run.font.size = Pt(10)
                elif ':' in ls and len(ls.split(':')[0]) < 20:
                    for run in p.runs:
                        run.font.name = 'Courier New'
                        run.font.size = Pt(10)

    # 푸터
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("\n© 2026 BLUE JEANS PICTURES")
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor(0x19, 0x19, 0x70)

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


# =================================================================
# [10] 진행 바
# =================================================================
def render_step_bar(step):
    labels = ["📄 업로드", "🔍 CHRIS", "🧹 SHIHO", "✍️ MOON"]
    dots = ""
    for i, label in enumerate(labels):
        cls = "done" if i < step else ("active" if i == step else "wait")
        sym = "✓" if i < step else str(i + 1)
        dots += (f'<div style="display:flex;flex-direction:column;align-items:center;gap:5px;">'
                 f'<div class="step-dot {cls}">{sym}</div>'
                 f'<div style="font-size:0.68rem;opacity:0.65;white-space:nowrap;">{label}</div></div>')
        if i < len(labels) - 1:
            lc = "done" if i < step - 1 else ""
            dots += f'<div class="step-line {lc}" style="margin-bottom:20px;"></div>'
    st.markdown(f'<div class="step-bar">{dots}</div>', unsafe_allow_html=True)


# =================================================================
# [11] 비서 카드
# =================================================================
def agent_card(emoji, name, role, desc, status, key, btn_label, btn_fn, result_fn, result_data):
    badge_map = {
        'waiting': '<span style="background:#E6E9EF;color:#888;padding:2px 10px;border-radius:20px;font-size:0.72rem;font-weight:800;">대기 중</span>',
        'active':  '<span style="background:#FFCB05;color:#191970;padding:2px 10px;border-radius:20px;font-size:0.72rem;font-weight:800;">● 준비됨</span>',
        'done':    '<span style="background:#2EC484;color:#FFFFFF;padding:2px 10px;border-radius:20px;font-size:0.72rem;font-weight:800;">✓ 완료</span>',
    }
    avatar_html = AVATAR_MAP.get(name, f'<div style="font-size:2.2rem;">{emoji}</div>')
    st.markdown(f"""
    <div class="agent-card {status}">
        <div style="display:flex;align-items:flex-start;gap:18px;">
            <div style="width:72px;height:72px;flex-shrink:0;border-radius:16px;overflow:hidden;">{avatar_html}</div>
            <div style="flex:1;">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:3px;">
                    <span style="font-size:1.15rem;font-weight:900;letter-spacing:0.04em;">{name}</span>
                    {badge_map[status]}
                </div>
                <div style="font-size:0.75rem;color:#B8860B;font-weight:700;margin-bottom:4px;">{role}</div>
                <div style="font-size:0.83rem;opacity:0.65;line-height:1.5;">{desc}</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)
    if status == 'active':
        if st.button(btn_label, key=f"{key}_btn", use_container_width=True):
            btn_fn()
    if status == 'done' and result_data:
        result_fn(result_data)


# =================================================================
# [12] 워크스페이스 페이지
# =================================================================
def show_workspace():
    st.markdown("""
    <div style="text-align:center;padding:1rem 0 0 0">
        <div style="font-size:0.85rem;font-weight:700;color:#191970;letter-spacing:0.15em;margin-bottom:0;font-family:'Paperlogy','Pretendard',sans-serif;">B L U E &nbsp; J E A N S &nbsp; P I C T U R E S</div>
        <div style="font-size:2.6rem;font-weight:900;color:#191970;font-family:'Playfair Display','Paperlogy','Georgia',serif;letter-spacing:-0.02em;margin-bottom:0.15rem;position:relative;display:inline-block;">REWRITE ENGINE</div>
        <div style="font-size:0.72rem;font-weight:600;letter-spacing:0.18em;color:#8E8E99;margin-top:0.1rem;">Y O U N G &nbsp; · &nbsp; V I N T A G E &nbsp; · &nbsp; F R E E &nbsp; · &nbsp; I N N O V A T I V E</div>
    </div>""", unsafe_allow_html=True)
    st.caption(f"집필: {ANTHROPIC_MODEL_WRITE} · 분석: {ANTHROPIC_MODEL_PLAN}")

    step = st.session_state.step
    render_step_bar(step)
    st.markdown('<hr>', unsafe_allow_html=True)

    client = get_client()

    # ── 업로드 ──
    if step == 0:
        if not st.session_state.get('_uploaded_ready'):
            uploaded = st.file_uploader("분석할 시나리오 PDF를 업로드하세요", type=["pdf"], key="pdf_uploader")
            if uploaded:
                with st.spinner("텍스트 추출 중..."):
                    text = extract_text(uploaded)
                if text:
                    st.session_state.raw_text = text
                    st.session_state['_uploaded_name'] = uploaded.name
                    st.session_state['_uploaded_kb'] = round(len(uploaded.getvalue()) / 1024)
                    st.session_state['_uploaded_chars'] = len(text)
                    st.session_state['_uploaded_ready'] = True
                    st.rerun()
        else:
            fname = st.session_state.get('_uploaded_name', '')
            kb = st.session_state.get('_uploaded_kb', 0)
            chars = st.session_state.get('_uploaded_chars', 0)
            st.markdown(f"""
            <div style="background:#EEF0FA;border:1px solid #C5D0F0;border-radius:12px;padding:16px 20px;margin-bottom:16px;display:flex;align-items:center;gap:14px;">
                <div style="font-size:2rem;">📄</div>
                <div style="flex:1;">
                    <div style="font-weight:800;font-size:0.95rem;">{safe(fname)}</div>
                    <div style="font-size:0.8rem;color:#666;margin-top:3px;">{kb:,} KB · {chars:,}자 추출 완료</div>
                </div>
                <div style="background:#2EC484;color:#FFFFFF;padding:4px 12px;border-radius:20px;font-size:0.75rem;font-weight:800;">✓ 준비완료</div>
            </div>""", unsafe_allow_html=True)
            _, c, _ = st.columns([2, 1, 2])
            with c:
                if st.button("분석 시작", use_container_width=True):
                    st.session_state.step = 1
                    st.session_state['_uploaded_ready'] = False
                    st.rerun()
            if st.button("다른 파일 선택"):
                for k in ['_uploaded_ready', '_uploaded_name', '_uploaded_kb', '_uploaded_chars']:
                    st.session_state.pop(k, None)
                st.session_state.raw_text = None
                st.rerun()
        return

    text = st.session_state.raw_text

    # ── CHRIS ──
    def do_chris():
        with st.spinner(f"CHRIS가 시나리오를 분석하고 있습니다 ({ANTHROPIC_MODEL_PLAN})..."):
            r = run_chris(text, client)
            if r:
                st.session_state.analysis = r
                st.session_state.step = 2
                st.rerun()
            else:
                st.error("분석 실패. 다시 시도해주세요.")

    chris_st = 'done' if st.session_state.analysis else 'active'
    agent_card("🔍", "CHRIS", "Senior Script Analyst",
               "구조 분석 · 15-Beat Sheet · 서사동력 · 장르 Rule Pack 진단",
               chris_st, "chris", "🔍 Chris 분석 시작", do_chris,
               render_analysis, st.session_state.analysis)

    if not st.session_state.analysis:
        agent_card("🧹", "SHIHO", "Script Doctor", "시퀀스 워싱 · 장르 재미 복구 · 대사 4축 분석", 'waiting', "shiho", "", lambda: None, lambda x: None, None)
        agent_card("✍️", "MOON", "Senior Screenwriter", "10개 씬 리라이팅 · Hook/Punch · 500자+", 'waiting', "moon", "", lambda: None, lambda x: None, None)
        return

    # ── SHIHO ──
    def do_shiho():
        with st.spinner(f"SHIHO가 시퀀스를 워싱하고 있습니다 ({ANTHROPIC_MODEL_PLAN})..."):
            r = run_shiho(text, st.session_state.analysis, client)
            if r:
                st.session_state.washing = r
                st.session_state.step = 3
                st.rerun()
            else:
                st.error("워싱 실패. 다시 시도해주세요.")

    shiho_st = 'done' if st.session_state.washing else 'active'
    agent_card("🧹", "SHIHO", "Script Doctor",
               "시퀀스 워싱 · 장르 재미 복구 · 대사 4축 분석 · 각색 제안 10가지",
               shiho_st, "shiho", "🧹 Shiho 워싱 시작", do_shiho,
               render_washing, st.session_state.washing)

    if not st.session_state.washing:
        agent_card("✍️", "MOON", "Senior Screenwriter", "10개 씬 리라이팅 · Hook/Punch · 500자+", 'waiting', "moon", "", lambda: None, lambda x: None, None)
        return

    # ── MOON ──
    def do_moon():
        with st.spinner(f"MOON이 각색 원고를 작성하고 있습니다 ({ANTHROPIC_MODEL_WRITE})..."):
            r = run_moon(text, st.session_state.analysis, st.session_state.washing, client)
            if r:
                st.session_state.rewriting = r
                full = {
                    **st.session_state.analysis,
                    'washing_table': st.session_state.washing.get('washing_table', []),
                    'suggestions': st.session_state.washing.get('suggestions', []),
                    'dialogue_analysis': st.session_state.washing.get('dialogue_analysis', {}),
                    'genre_fun_recovery': st.session_state.washing.get('genre_fun_recovery', {}),
                    'rewriting': r.get('rewriting', {})
                }
                st.session_state.db.insert(0, full)
                st.session_state.selected_item = full
                st.session_state.step = 4
                st.rerun()
            else:
                st.error("리라이팅 실패. 다시 시도해주세요.")

    moon_st = 'done' if st.session_state.rewriting else 'active'
    agent_card("✍️", "MOON", "Senior Screenwriter",
               "진단 연결 리라이팅 · Hook/Punch 필수 · 500자+ · 10개 씬",
               moon_st, "moon", "✍️ Moon 리라이팅 시작", do_moon,
               render_rewriting, st.session_state.rewriting)

    # ── 완료 ──
    if st.session_state.step == 4 and st.session_state.selected_item:
        st.markdown('<hr>', unsafe_allow_html=True)
        st.markdown('<div style="text-align:center;padding:16px 0;"><span style="font-size:1.4rem;font-weight:900;color:#2EC484;">모든 분석 완료!</span></div>', unsafe_allow_html=True)
        item = st.session_state.selected_item
        c1, c2, c3 = st.columns(3)
        with c1:
            title = re.sub(r'[/*?:"<>|]', '_', item.get('title', '제목없음'))
            try:
                docx_bytes = create_docx(item)
                st.download_button(
                    "보고서 다운로드 (DOCX)", data=docx_bytes,
                    file_name=get_report_filename(item.get('title', '')),
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key="btn_download_docx", use_container_width=True
                )
            except Exception as e:
                st.error(f"DOCX 생성 오류: {e}")
        with c2:
            if st.button("목록으로", key="btn_to_index", use_container_width=True):
                st.session_state.page = "index"
                st.rerun()
        with c3:
            if st.button("새 시나리오 분석", key="btn_new", use_container_width=True):
                for k in ['step', 'raw_text', 'analysis', 'washing', 'rewriting', 'selected_item']:
                    st.session_state[k] = 0 if k == 'step' else None
                st.rerun()


# =================================================================
# [13] 갤러리 페이지 (홈)
# =================================================================
def show_index():
    st.markdown("""
    <div style="text-align:center;padding:60px 0 36px;">
        <div style="font-size:0.72rem;font-weight:900;letter-spacing:0.5em;color:#FFCB05;">BLUE JEANS PICTURES</div>
        <div style="font-size:3.6rem;font-weight:950;color:#191970;line-height:1;letter-spacing:-0.03em;margin:10px 0;">REWRITE ENGINE</div>
        <div style="font-size:0.78rem;letter-spacing:0.2em;opacity:0.35;">v2.0 · YOUNG · VINTAGE · FREE · INNOVATIVE</div>
    </div>""", unsafe_allow_html=True)

    _, c, _ = st.columns([1, 1, 1])
    with c:
        if st.button("+ 새 시나리오 분석하기", use_container_width=True):
            for k in ['step', 'raw_text', 'analysis', 'washing', 'rewriting']:
                st.session_state[k] = 0 if k == 'step' else None
            st.session_state.page = "workspace"
            st.rerun()

    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown("### 검토 보고서 아카이브")

    if not st.session_state.db:
        st.markdown('<div style="text-align:center;padding:60px 0;opacity:0.3;"><div style="font-size:3rem;margin-bottom:10px;">🎬</div><div>아직 분석된 시나리오가 없습니다.</div></div>', unsafe_allow_html=True)
    else:
        cols = st.columns(3)
        for idx, item in enumerate(st.session_state.db):
            with cols[idx % 3]:
                img_url = get_genre_img_url(item)
                genre_info = item.get('genre', {})
                genre_label = genre_info.get('primary', '') if isinstance(genre_info, dict) else str(genre_info)
                score_val = item.get('mark', {}).get('final', 0)
                score_color = C_GREEN if float(score_val) >= 7 else (C_YELLOW if float(score_val) >= 5 else C_RED)
                st.markdown(f"""
                <div class="gallery-card">
                    <img class="gallery-card-img" src="{img_url}" onerror="this.style.display='none'" alt="">
                    <div class="gallery-card-body">
                        <div style="font-size:0.65rem;font-weight:700;color:#888;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;">{safe(genre_label)}</div>
                        <div style="font-weight:900;font-size:1rem;margin-bottom:10px;line-height:1.3;">{safe(item.get('title', 'Untitled'))}</div>
                        <div style="font-size:1.6rem;font-weight:950;color:{score_color};">{score_val}<span style="font-size:0.65rem;color:#888;"> /10.0</span></div>
                    </div>
                </div>""", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("보기", key=f"v_{idx}", use_container_width=True):
                        st.session_state.selected_item = item
                        st.session_state.analysis = item
                        st.session_state.washing = {
                            'washing_table': item.get('washing_table', []),
                            'dialogue_analysis': item.get('dialogue_analysis', {}),
                            'suggestions': item.get('suggestions', []),
                            'genre_fun_recovery': item.get('genre_fun_recovery', {}),
                        }
                        st.session_state.rewriting = {'rewriting': item.get('rewriting', {})}
                        st.session_state.step = 4
                        st.session_state.page = "workspace"
                        st.rerun()
                with c2:
                    if st.button("삭제", key=f"d_{idx}", use_container_width=True):
                        st.session_state.db.pop(idx)
                        st.rerun()


# =================================================================
# [14] 실행
# =================================================================
apply_design()

if st.session_state.page == "index":
    show_index()
elif st.session_state.page == "workspace":
    show_workspace()

st.markdown(
    '<div style="text-align:center;font-size:0.65rem;padding:40px 0 16px;letter-spacing:2px;opacity:0.25;">© 2026 BLUE JEANS PICTURES</div>',
    unsafe_allow_html=True
)
