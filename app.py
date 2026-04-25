import streamlit as st
import re
from utils import extract_text_from_pdf, keyword_match, generate_suggestions

st.set_page_config(
    page_title="AI Resume Scanner",
    page_icon="📄",
    layout="wide"
)

# ---------- THEME STATE ----------
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode

dark = st.session_state.dark_mode

# ---------- THEME VARIABLES ----------
if dark:
    bg        = "#0f0f13"
    card_bg   = "#16161d"
    border    = "#2a2a35"
    text      = "#e8e8f0"
    subtext   = "#6b7280"
    sidebar_bg= "#16161d"
    sidebar_t = "#c0c0d0"
    bar_bg    = "#2a2a35"
    suggestion_bg = "#1a1a25"
    suggestion_border = "#a78bfa"
    suggestion_text = "#c4c4d8"
    input_bg  = "#16161d"
    input_border = "#2a2a35"
    input_text = "#e8e8f0"
    toggle_icon = "☀️"
    toggle_label = "Light Mode"
else:
    bg        = "#f6f7fb"
    card_bg   = "#ffffff"
    border    = "#e5e7eb"
    text      = "#1f2937"
    subtext   = "#6b7280"
    sidebar_bg= "#f0f1f8"
    sidebar_t = "#374151"
    bar_bg    = "#e5e7eb"
    suggestion_bg = "#f5f3ff"
    suggestion_border = "#7c3aed"
    suggestion_text = "#4b5563"
    input_bg  = "#ffffff"
    input_border = "#d1d5db"
    input_text = "#1f2937"
    toggle_icon = "🌙"
    toggle_label = "Dark Mode"

# ---------- CUSTOM CSS ----------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

* {{ font-family: 'DM Sans', sans-serif; }}

h1, h2, h3 {{ font-family: 'Syne', sans-serif !important; }}

.stApp {{
    background: {bg};
    color: {text};
}}

/* Sidebar */
[data-testid="stSidebar"] {{
    background: {sidebar_bg} !important;
    border-right: 1px solid {border};
}}
[data-testid="stSidebar"] * {{ color: {sidebar_t} !important; }}

/* Title */
.hero-title {{
    font-family: 'Syne', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    line-height: 1.1;
    margin-bottom: 0.25rem;
}}

.hero-sub {{
    text-align: center;
    color: {subtext};
    font-size: 1.05rem;
    margin-bottom: 2rem;
    font-weight: 300;
}}

/* Cards */
.card {{
    background: {card_bg};
    border: 1px solid {border};
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
}}

/* Score display */
.score-ring-container {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    padding: 24px;
}

.score-number {
    font-family: 'Syne', sans-serif;
    font-size: 4rem;
    font-weight: 800;
    line-height: 1;
}

.score-label {
    font-size: 0.85rem;
    color: #6b7280;
    margin-top: 4px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* Score colors */
.score-high { color: #34d399; }
.score-mid  { color: #fbbf24; }
.score-low  { color: #f87171; }

/* Category score bars */
.cat-bar-bg {{
    background: {bar_bg};
    border-radius: 99px;
    height: 8px;
    margin: 6px 0 14px 0;
    overflow: hidden;
}}
.cat-bar-fill {{
    height: 8px;
    border-radius: 99px;
    transition: width 0.6s ease;
}}

/* Keyword chips */
.chip-found {{
    display: inline-block;
    background: #052e16;
    color: #34d399;
    border: 1px solid #166534;
    border-radius: 99px;
    padding: 4px 14px;
    margin: 4px;
    font-size: 0.85rem;
    font-weight: 500;
}}
.chip-missing {{
    display: inline-block;
    background: #2d0a0a;
    color: #f87171;
    border: 1px solid #7f1d1d;
    border-radius: 99px;
    padding: 4px 14px;
    margin: 4px;
    font-size: 0.85rem;
    font-weight: 500;
}}

/* Suggestion card */
.suggestion-card {{
    background: {suggestion_bg};
    border-left: 3px solid {suggestion_border};
    border-radius: 0 12px 12px 0;
    padding: 14px 18px;
    margin-bottom: 10px;
    font-size: 0.95rem;
    color: {suggestion_text};
}}

/* ATS warning */
.ats-warn {{
    background: #1c1400;
    border: 1px solid #78350f;
    border-radius: 10px;
    padding: 12px 16px;
    color: #fbbf24;
    margin-bottom: 8px;
    font-size: 0.9rem;
}}
.ats-ok {{
    background: #052e16;
    border: 1px solid #166534;
    border-radius: 10px;
    padding: 12px 16px;
    color: #34d399;
    margin-bottom: 8px;
    font-size: 0.9rem;
}}

/* Section headers */
.section-header {{
    font-family: 'Syne', sans-serif;
    font-size: 1.2rem;
    font-weight: 700;
    color: {text};
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
}}

/* Upload & textarea overrides */
[data-testid="stFileUploader"] {{
    background: {input_bg} !important;
    border: 2px dashed {border} !important;
    border-radius: 14px !important;
}}
textarea {{
    background-color: {input_bg} !important;
    border: 1px solid {input_border} !important;
    color: {input_text} !important;
    border-radius: 10px !important;
}}

/* Button */
.stButton>button {{
    background: linear-gradient(135deg, #7c3aed, #2563eb);
    color: white;
    border-radius: 10px;
    height: 3em;
    font-size: 16px;
    border: none;
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    width: 100%;
    transition: opacity 0.2s;
}}
.stButton>button:hover {{ opacity: 0.85; }}

/* Toggle button */
.toggle-btn>button {{
    background: {card_bg} !important;
    color: {text} !important;
    border: 1px solid {border} !important;
    border-radius: 99px !important;
    padding: 4px 16px !important;
    font-size: 0.85rem !important;
    height: 2.2em !important;
    width: auto !important;
}}

/* Divider */
hr {{ border-color: {border} !important; }}

/* Info/metric overrides */
[data-testid="stMetric"] {{
    background: {card_bg};
    border: 1px solid {border};
    border-radius: 12px;
    padding: 16px;
}}

.stAlert {{ border-radius: 10px !important; }}

.strength-label {{
    font-size: 0.8rem;
    color: {subtext};
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}
</style>
""", unsafe_allow_html=True)


# ---------- HELPERS ----------

def get_score_class(score):
    if score >= 70:
        return "score-high"
    elif score >= 40:
        return "score-mid"
    return "score-low"


def score_color(score):
    if score >= 70:
        return "#34d399"
    elif score >= 40:
        return "#fbbf24"
    return "#f87171"


def score_label(score):
    if score >= 70:
        return "Strong Match ✅"
    elif score >= 40:
        return "Moderate Match ⚡"
    return "Weak Match ❌"


def check_resume_strength(text):
    """Score the resume itself for quality signals."""
    issues = []
    score = 100

    word_count = len(text.split())
    if word_count < 200:
        issues.append("Resume seems too short (less than 200 words)")
        score -= 20
    elif word_count > 1000:
        issues.append("Resume may be too long (over 1000 words)")
        score -= 10

    action_verbs = ["developed", "built", "led", "managed", "designed", "created",
                    "implemented", "improved", "achieved", "delivered", "launched",
                    "increased", "reduced", "optimized", "analyzed", "collaborated"]
    found_verbs = [v for v in action_verbs if v in text.lower()]
    if len(found_verbs) < 3:
        issues.append("Few action verbs detected — use words like 'built', 'led', 'delivered'")
        score -= 20

    if not re.search(r'\d+', text):
        issues.append("No numbers/metrics found — quantify achievements (e.g., '30% faster')")
        score -= 20

    return max(score, 0), issues


def check_ats_compatibility(text):
    """Basic ATS checks."""
    warnings = []
    if len(text) < 100:
        warnings.append("Very little text extracted — resume may use images or complex formatting that ATS can't read")
    if re.search(r'[│┤╡╢╖╕╣║╗╝╜╛╔╩╦╠═╬╧╨╤╥╙╘╒╓╫╪┘┌█▄▌▐▀]', text):
        warnings.append("Special box/table characters detected — may not parse correctly in ATS")
    return warnings


def category_scores(resume_text, job_description):
    """Rough category breakdown scores."""
    categories = {
        "Skills & Tech": ["python", "javascript", "sql", "react", "aws", "docker", "api",
                          "machine learning", "data", "cloud", "java", "typescript", "git"],
        "Experience": ["experience", "years", "worked", "developed", "built", "led",
                       "managed", "delivered", "launched"],
        "Education": ["bachelor", "master", "degree", "university", "college",
                      "certification", "certified", "diploma", "phd"],
    }
    job_lower = job_description.lower()
    resume_lower = resume_text.lower()
    results = {}
    for cat, keywords in categories.items():
        job_hits = [k for k in keywords if k in job_lower]
        if not job_hits:
            results[cat] = None
            continue
        resume_hits = [k for k in job_hits if k in resume_lower]
        results[cat] = round(len(resume_hits) / len(job_hits) * 100)
    return results


def get_found_keywords(resume_text, job_description):
    """Return keywords from JD that ARE in the resume."""
    words = set(re.findall(r'\b[a-zA-Z]{3,}\b', job_description.lower()))
    stopwords = {"the", "and", "for", "with", "that", "this", "are", "you",
                 "will", "have", "has", "from", "your", "our", "not", "but",
                 "can", "all", "was", "they", "their", "also", "any", "its"}
    resume_lower = resume_text.lower()
    found = [w for w in words if w in resume_lower and w not in stopwords]
    return sorted(found)


def generate_report_text(score, category_scores, missing_keywords, suggestions, ats_warnings, strength_score):
    """Generate plain text report for download."""
    lines = [
        "AI RESUME SCANNER — ANALYSIS REPORT",
        "=" * 40,
        f"Overall Match Score: {score}%  ({score_label(score)})",
        f"Resume Strength:     {strength_score}%",
        "",
        "CATEGORY BREAKDOWN",
        "-" * 30,
    ]
    for cat, val in category_scores.items():
        if val is not None:
            lines.append(f"  {cat}: {val}%")
    lines += ["", "MISSING KEYWORDS", "-" * 30]
    if missing_keywords:
        for kw in missing_keywords:
            lines.append(f"  ⚠ {kw}")
    else:
        lines.append("  None — all keywords found!")
    lines += ["", "IMPROVEMENT SUGGESTIONS", "-" * 30]
    for s in suggestions:
        lines.append(f"  • {s}")
    if ats_warnings:
        lines += ["", "ATS WARNINGS", "-" * 30]
        for w in ats_warnings:
            lines.append(f"  ⚠ {w}")
    lines += ["", "=" * 40, "Generated by AI Resume Scanner"]
    return "\n".join(lines)


# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("### ⚙️ Settings & Tips")
    st.markdown("<div class='toggle-btn'>", unsafe_allow_html=True)
    st.button(f"{toggle_icon} {toggle_label}", on_click=toggle_theme, key="theme_toggle")
    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()
    st.markdown("**How to get a better score:**")
    st.markdown("- Mirror keywords from the job description\n- Quantify your achievements\n- Use action verbs\n- Keep formatting ATS-friendly")
    st.divider()
    st.markdown("**Score Guide**")
    st.markdown("🟢 70%+ → Strong Match\n🟡 40–69% → Moderate\n🔴 <40% → Needs Work")
    st.divider()
    st.caption("Built with Streamlit · TF-IDF & NLP")


# ---------- HERO ----------
st.markdown("<div class='hero-title'>📄 AI Resume Scanner</div>", unsafe_allow_html=True)
st.markdown("<p class='hero-sub'>Check how well your resume matches any job description — instantly</p>", unsafe_allow_html=True)

st.divider()

# ---------- INPUTS ----------
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("<div class='section-header'>📎 Upload Resume</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="collapsed")

with col2:
    st.markdown("<div class='section-header'>📋 Job Description</div>", unsafe_allow_html=True)
    job_description = st.text_area("Paste job description here", height=180, label_visibility="collapsed",
                                   placeholder="Paste the full job description here...")

st.divider()

_, btn_col, _ = st.columns([2, 1, 2])
with btn_col:
    analyze = st.button("🔍 Analyze Resume")

# ---------- ANALYSIS ----------
if uploaded_file and job_description and analyze:

    with st.spinner("Analyzing your resume..."):
        resume_text = extract_text_from_pdf(uploaded_file)
        score, missing_keywords = keyword_match(resume_text, job_description)
        suggestions = generate_suggestions(missing_keywords)
        cat_scores = category_scores(resume_text, job_description)
        found_keywords = get_found_keywords(resume_text, job_description)
        strength_score, strength_issues = check_resume_strength(resume_text)
        ats_warnings = check_ats_compatibility(resume_text)
        report_text = generate_report_text(score, cat_scores, missing_keywords,
                                           suggestions, ats_warnings, strength_score)

    st.divider()

    # --- ROW 1: Score + Categories ---
    col_score, col_cats = st.columns([1, 2], gap="large")

    with col_score:
        sc = get_score_class(score)
        st.markdown(f"""
        <div class='card score-ring-container'>
            <div class='score-number {sc}'>{score}%</div>
            <div class='score-label'>Match Score</div>
            <div style='margin-top:10px; font-size:0.9rem; color:#9ca3af'>{score_label(score)}</div>
        </div>
        """, unsafe_allow_html=True)

        # Resume strength
        s_color = score_color(strength_score)
        st.markdown(f"""
        <div class='card'>
            <div class='section-header'>💪 Resume Strength</div>
            <div style='font-size:2rem; font-weight:800; color:{s_color}; font-family:Syne,sans-serif'>{strength_score}%</div>
            <div class='cat-bar-bg'><div class='cat-bar-fill' style='width:{strength_score}%; background:{s_color}'></div></div>
        </div>
        """, unsafe_allow_html=True)
        if strength_issues:
            for issue in strength_issues:
                st.markdown(f"<div class='ats-warn'>⚠️ {issue}</div>", unsafe_allow_html=True)

    with col_cats:
        st.markdown("<div class='section-header'>📊 Score Breakdown by Category</div>", unsafe_allow_html=True)
        for cat, val in cat_scores.items():
            if val is None:
                continue
            c = score_color(val)
            st.markdown(f"""
            <div style='margin-bottom:6px'>
                <div style='display:flex; justify-content:space-between; font-size:0.9rem; color:#9ca3af'>
                    <span>{cat}</span><span style='color:{c}; font-weight:600'>{val}%</span>
                </div>
                <div class='cat-bar-bg'>
                    <div class='cat-bar-fill' style='width:{val}%; background:{c}'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ATS check
        st.markdown("<div class='section-header' style='margin-top:20px'>🤖 ATS Compatibility</div>", unsafe_allow_html=True)
        if ats_warnings:
            for w in ats_warnings:
                st.markdown(f"<div class='ats-warn'>⚠️ {w}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='ats-ok'>✅ No ATS issues detected — your resume looks clean!</div>", unsafe_allow_html=True)

    st.divider()

    # --- ROW 2: Keywords ---
    col_found, col_missing = st.columns(2, gap="large")

    with col_found:
        st.markdown(f"<div class='section-header'>✅ Found Keywords ({len(found_keywords)})</div>", unsafe_allow_html=True)
        if found_keywords:
            chips = " ".join([f"<span class='chip-found'>{k}</span>" for k in found_keywords[:20]])
            st.markdown(chips, unsafe_allow_html=True)
        else:
            st.caption("No matching keywords found.")

    with col_missing:
        st.markdown(f"<div class='section-header'>🚨 Missing Keywords ({len(missing_keywords)})</div>", unsafe_allow_html=True)
        if missing_keywords:
            chips = " ".join([f"<span class='chip-missing'>{k}</span>" for k in missing_keywords])
            st.markdown(chips, unsafe_allow_html=True)
        else:
            st.markdown("<div class='ats-ok'>✅ Your resume contains all required keywords!</div>", unsafe_allow_html=True)

    st.divider()

    # --- ROW 3: Suggestions + Download ---
    st.markdown("<div class='section-header'>✨ Improvement Suggestions</div>", unsafe_allow_html=True)
    for s in suggestions:
        st.markdown(f"<div class='suggestion-card'>💡 {s}</div>", unsafe_allow_html=True)

    st.divider()

    # Download report
    st.download_button(
        label="📥 Download Full Report",
        data=report_text,
        file_name="resume_analysis_report.txt",
        mime="text/plain"
    )

elif not uploaded_file or not job_description:
    st.markdown("""
    <div style='text-align:center; color:#4b5563; padding: 40px 0; font-size:1rem'>
        Upload your resume and paste a job description above, then click <strong style='color:#a78bfa'>Analyze Resume</strong>
    </div>
    """, unsafe_allow_html=True)

# ---------- FOOTER ----------
st.divider()
st.markdown("<div style='text-align:center; color:#374151; font-size:0.8rem'>AI Resume Scanner · Built with Streamlit & NLP</div>", unsafe_allow_html=True)