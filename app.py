import streamlit as st
import google.generativeai as genai
import json
import re
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VerifyAI – Fake News Detector",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

:root {
    --bg:       #0d0f14;
    --surface:  #161923;
    --border:   #252b38;
    --accent:   #00e5ff;
    --danger:   #ff4757;
    --warn:     #ffa502;
    --safe:     #2ed573;
    --muted:    #8892a4;
    --text:     #e8eaf0;
}

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp { background-color: var(--bg) !important; }

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

.hero {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2rem;
}
.hero h1 {
    font-weight: 800;
    font-size: 3rem;
    letter-spacing: -1px;
    background: linear-gradient(135deg, var(--accent) 0%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}
.hero p {
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    color: var(--muted);
    margin-top: 0.5rem;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
}

.score-badge {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 0.6rem 1.4rem;
    border-radius: 50px;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    font-size: 1.1rem;
    margin: 0.5rem 0;
}
.score-fake   { background: rgba(255,71,87,0.15);  color: var(--danger); border: 1px solid var(--danger); }
.score-warn   { background: rgba(255,165,2,0.15);  color: var(--warn);   border: 1px solid var(--warn); }
.score-legit  { background: rgba(46,213,115,0.15); color: var(--safe);   border: 1px solid var(--safe); }

.bar-container { background: var(--border); border-radius: 6px; height: 10px; margin: 6px 0 14px; }
.bar-fill      { height: 10px; border-radius: 6px; transition: width 0.8s ease; }

.tag {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-family: 'Space Mono', monospace;
    margin: 3px;
    border: 1px solid;
}
.tag-red    { background: rgba(255,71,87,0.1);  color: var(--danger); border-color: var(--danger); }
.tag-yellow { background: rgba(255,165,2,0.1);  color: var(--warn);   border-color: var(--warn); }
.tag-green  { background: rgba(46,213,115,0.1); color: var(--safe);   border-color: var(--safe); }
.tag-blue   { background: rgba(0,229,255,0.1);  color: var(--accent); border-color: var(--accent); }

.metric-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
.metric-box  {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
}
.metric-val  { font-size: 2rem; font-weight: 800; font-family: 'Space Mono', monospace; }
.metric-lbl  { font-size: 0.7rem; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; margin-top: 2px; }

.sec-head {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--muted);
    font-family: 'Space Mono', monospace;
    margin-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
    padding-bottom: 6px;
}

.stTextArea textarea, .stTextInput input {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.85rem !important;
}

.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #00e5ff22, #a78bfa22) !important;
    border: 1px solid var(--accent) !important;
    color: var(--accent) !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    padding: 0.7rem !important;
    letter-spacing: 1px;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; max-width: 1100px; }
</style>
""", unsafe_allow_html=True)


# ─── Helpers ─────────────────────────────────────────────────────────────────
def score_class(score: int) -> str:
    if score < 40:
        return "score-fake"
    if score < 65:
        return "score-warn"
    return "score-legit"

def score_color(score: int) -> str:
    if score < 40:
        return "#ff4757"
    if score < 65:
        return "#ffa502"
    return "#2ed573"

def tag_class_for_assessment(assessment: str) -> str:
    a = assessment.upper()
    if "FALSE" in a:
        return "tag-red"
    if "UNCERTAIN" in a:
        return "tag-yellow"
    return "tag-green"


# ─── Gemini Setup ─────────────────────────────────────────────────────────────
def get_gemini_model(api_key: str):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")


# ─── Analysis Function ────────────────────────────────────────────────────────
def analyze_article(model, text: str, source: str = "") -> dict:
    prompt = f"""
You are an expert fact-checker and media literacy educator. Analyze the following news article/content for credibility.

Article/Content:
\"\"\"
{text}
\"\"\"

Source (if provided): {source if source else "Not provided"}

Return ONLY a valid JSON object with this exact structure:
{{
  "credibility_score": <integer 0-100>,
  "verdict": "<LIKELY FAKE | MISLEADING | UNVERIFIED | MOSTLY CREDIBLE | CREDIBLE>",
  "confidence": "<LOW | MEDIUM | HIGH>",
  "summary": "<2-3 sentence neutral summary>",
  "red_flags": ["<flag1>", "<flag2>"],
  "positive_signals": ["<signal1>"],
  "key_claims": [
    {{"claim": "<claim>", "assessment": "<LIKELY TRUE | UNCERTAIN | LIKELY FALSE>", "reason": "<brief reason>"}}
  ],
  "emotional_language_score": <0-100>,
  "source_credibility": "<UNKNOWN | LOW | MEDIUM | HIGH>",
  "recommendations": ["<tip1>", "<tip2>"],
  "category": "<Politics | Health | Science | Finance | Entertainment | Sports | Technology | Other>"
}}
"""
    response = model.generate_content(prompt)
    raw = response.text.strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"```$", "", raw).strip()
    return json.loads(raw)


# ─── Session State ────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "result" not in st.session_state:
    st.session_state.result = None
if "last_source" not in st.session_state:
    st.session_state.last_source = ""
if "last_text" not in st.session_state:
    st.session_state.last_text = ""


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## VerifyAI")
    st.markdown("AI Fact Check Assistant")
    st.markdown("---")
    st.markdown("### About")
    st.markdown(
        "VerifyAI analyzes news articles for credibility signals, "
        "emotional manipulation, and factual consistency using Gemini AI."
    )
    if st.session_state.history:
        st.markdown("### Recent Checks")
        for h in reversed(st.session_state.history[-5:]):
            color = score_color(h["score"])
            st.markdown(
                f'<span style="color:{color};font-family:Space Mono,monospace;font-size:0.8rem;">'
                f'[{h["score"]}]</span> {h["preview"]}',
                unsafe_allow_html=True
            )


# ─── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>VerifyAI</h1>
  <p>AI-Powered Fake News Detector &nbsp;·&nbsp; Powered by Gemini</p>
</div>
""", unsafe_allow_html=True)


# ─── Main Layout ──────────────────────────────────────────────────────────────
col_input, col_result = st.columns([1, 1.1], gap="large")

with col_input:
    st.markdown('<div class="sec-head">Article Input</div>', unsafe_allow_html=True)

    source_url = st.text_input(
        "Source / URL (optional)",
        placeholder="https://example.com/article"
    )

    article_text = st.text_area(
        "Paste article text",
        height=320,
        placeholder="Paste the full article or news content here..."
    )

    analyze_btn = st.button("Analyze Article")


# ─── Analysis Logic ───────────────────────────────────────────────────────────
if analyze_btn:
    if not API_KEY:
        st.error("GOOGLE_API_KEY not found. Add it to your .env file.")
    elif not article_text.strip():
        st.error("Please paste article text to analyze.")
    else:
        with st.spinner("Analyzing with Gemini AI..."):
            try:
                model = get_gemini_model(API_KEY)
                result = analyze_article(model, article_text, source_url)
                st.session_state.result = result
                st.session_state.last_source = source_url
                st.session_state.last_text = article_text

                st.session_state.history.append({
                    "preview": article_text[:40] + "...",
                    "score": result["credibility_score"],
                    "timestamp": datetime.now().strftime("%H:%M")
                })

            except json.JSONDecodeError:
                st.error("Failed to parse AI response. Please try again.")
            except Exception as e:
                st.error(str(e))


# ─── Display Results ──────────────────────────────────────────────────────────
with col_result:
    if st.session_state.result:
        r = st.session_state.result
        score = r["credibility_score"]
        s_cls = score_class(score)
        s_col = score_color(score)

        # ── Verdict Badge ──
        st.markdown(
            f'<div class="score-badge {s_cls}">{r["verdict"]}</div>',
            unsafe_allow_html=True
        )

        # ── Metric Grid ──
        emo = r.get("emotional_language_score", 0)
        src_cred = r.get("source_credibility", "UNKNOWN")
        st.markdown(f"""
        <div class="metric-grid">
          <div class="metric-box">
            <div class="metric-val" style="color:{s_col}">{score}</div>
            <div class="metric-lbl">Credibility</div>
          </div>
          <div class="metric-box">
            <div class="metric-val" style="color:#ffa502">{emo}</div>
            <div class="metric-lbl">Emotional Score</div>
          </div>
          <div class="metric-box">
            <div class="metric-val" style="color:var(--accent);font-size:1.1rem">{r['confidence']}</div>
            <div class="metric-lbl">Confidence</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Credibility Bar ──
        st.markdown(f"""
        <div style="margin: 1rem 0 0.3rem;">
          <span class="sec-head">Credibility Score</span>
        </div>
        <div class="bar-container">
          <div class="bar-fill" style="width:{score}%; background:{s_col};"></div>
        </div>
        """, unsafe_allow_html=True)

        # ── Tags Row ──
        cat = r.get("category", "Other")
        st.markdown(
            f'<span class="tag tag-blue">{cat}</span>'
            f'<span class="tag tag-blue">Source: {src_cred}</span>',
            unsafe_allow_html=True
        )
        st.markdown("")

        # ── Summary ──
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-head">Summary</div>', unsafe_allow_html=True)
        st.write(r["summary"])
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Red Flags & Positive Signals ──
        col_flags, col_pos = st.columns(2)
        with col_flags:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="sec-head">Red Flags</div>', unsafe_allow_html=True)
            flags = r.get("red_flags", [])
            if flags:
                for f in flags:
                    st.markdown(f'<span class="tag tag-red">{f}</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span style="color:var(--muted);font-size:0.85rem">None detected</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_pos:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="sec-head">Positive Signals</div>', unsafe_allow_html=True)
            signals = r.get("positive_signals", [])
            if signals:
                for s in signals:
                    st.markdown(f'<span class="tag tag-green">{s}</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span style="color:var(--muted);font-size:0.85rem">None detected</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Key Claims ──
        claims = r.get("key_claims", [])
        if claims:
            st.markdown('<div class="sec-head" style="margin-top:0.5rem">Key Claims</div>', unsafe_allow_html=True)
            for c in claims:
                t_cls = tag_class_for_assessment(c["assessment"])
                st.markdown(f"""
                <div class="card" style="margin-bottom:0.6rem">
                  <span class="tag {t_cls}">{c['assessment']}</span>
                  <div style="margin-top:0.5rem;font-size:0.9rem"><strong>{c['claim']}</strong></div>
                  <div style="font-size:0.8rem;color:var(--muted);margin-top:0.3rem">{c['reason']}</div>
                </div>
                """, unsafe_allow_html=True)

        # ── Recommendations ──
        recs = r.get("recommendations", [])
        if recs:
            st.markdown('<div class="sec-head" style="margin-top:0.5rem">Recommendations</div>', unsafe_allow_html=True)
            st.markdown('<div class="card">', unsafe_allow_html=True)
            for rec in recs:
                st.markdown(f'<div style="font-size:0.85rem;margin-bottom:0.4rem">· {rec}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Export ──
        export_data = {
            "analyzed_at": datetime.now().isoformat(),
            "source": st.session_state.last_source,
            "article_preview": st.session_state.last_text[:200],
            "analysis": r
        }
        st.download_button(
            label="Export Results as JSON",
            data=json.dumps(export_data, indent=2),
            file_name="verify_ai_result.json",
            mime="application/json"
        )

    else:
        st.markdown("""
        <div class="card" style="text-align:center;padding:3rem 1.5rem;">
          <div style="font-size:2.5rem;margin-bottom:1rem;opacity:0.3">◎</div>
          <div style="font-family:'Space Mono',monospace;font-size:0.8rem;color:var(--muted);letter-spacing:2px;text-transform:uppercase;">
            Paste an article and click<br>Analyze Article to begin
          </div>
        </div>
        """, unsafe_allow_html=True)