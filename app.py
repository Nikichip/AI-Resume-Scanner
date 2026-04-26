import streamlit as st
import re
import requests
from utils import extract_text_from_pdf, keyword_match, generate_suggestions

# ---------- DOCX SUPPORT ----------
def extract_text_from_docx(file):
    try:
        import docx
        doc = docx.Document(file)
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    except Exception:
        return ""

st.set_page_config(page_title="AI Resume Scanner", page_icon="📄", layout="wide")

# ---------- SESSION STATE ----------
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "history" not in st.session_state:
    st.session_state.history = []
if "cover_letter" not in st.session_state:
    st.session_state.cover_letter = None
if "rewrite_bullets" not in st.session_state:
    st.session_state.rewrite_bullets = None

def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode

dark = st.session_state.dark_mode

# ---------- THEME ----------
if dark:
    bg = "#0f0f13"; card_bg = "#16161d"; border = "#2a2a35"; text = "#e8e8f0"
    subtext = "#6b7280"; sidebar_bg = "#16161d"; sidebar_t = "#c0c0d0"; bar_bg = "#2a2a35"
    suggestion_bg = "#1a1a25"; suggestion_border = "#a78bfa"; suggestion_text = "#c4c4d8"
    input_bg = "#16161d"; input_text = "#e8e8f0"; preview_bg = "#12121a"
    chip_found_bg="#052e16"; chip_found_color="#34d399"; chip_found_border="#166534"
    chip_missing_bg="#2d0a0a"; chip_missing_color="#f87171"; chip_missing_border="#7f1d1d"
    chip_cat_bg="#1a1030"; chip_cat_color="#a78bfa"; chip_cat_border="#4c1d95"
    chip_tool_bg="#0a1a2d"; chip_tool_color="#60a5fa"; chip_tool_border="#1e3a5f"
    chip_soft_bg="#0a1f0a"; chip_soft_color="#86efac"; chip_soft_border="#14532d"
    ats_ok_bg="#052e16"; ats_ok_border="#166534"; ats_ok_color="#34d399"
    ats_warn_bg="#1c1400"; ats_warn_border="#78350f"; ats_warn_color="#fbbf24"
    toggle_icon = "☀️"; toggle_label = "Light Mode"
    upload_bg = "#16161d"; upload_border = "#2a2a35"
    browse_bg = "#2a2a35"; browse_color = "#a78bfa"; browse_border = "#3b3b52"
    sidebar_btn_bg = "#1e1e2e"; sidebar_btn_color = "#a78bfa"; sidebar_btn_border = "#3b3b52"
    sidebar_btn_hover = "#2a2a40"
    textarea_bg = "#16161d"; textarea_border = "#2a2a35"
else:
    bg = "#f6f7fb"; card_bg = "#ffffff"; border = "#e5e7eb"; text = "#1f2937"
    subtext = "#6b7280"; sidebar_bg = "#f0f1f8"; sidebar_t = "#374151"; bar_bg = "#e5e7eb"
    suggestion_bg = "#f5f3ff"; suggestion_border = "#7c3aed"; suggestion_text = "#4b5563"
    input_bg = "#ffffff"; input_text = "#1f2937"; preview_bg = "#f9f9fb"
    chip_found_bg="#f0fdf4"; chip_found_color="#15803d"; chip_found_border="#86efac"
    chip_missing_bg="#fff1f2"; chip_missing_color="#be123c"; chip_missing_border="#fecdd3"
    chip_cat_bg="#faf5ff"; chip_cat_color="#6d28d9"; chip_cat_border="#ddd6fe"
    chip_tool_bg="#eff6ff"; chip_tool_color="#1d4ed8"; chip_tool_border="#bfdbfe"
    chip_soft_bg="#f0fdf4"; chip_soft_color="#15803d"; chip_soft_border="#bbf7d0"
    ats_ok_bg="#f0fdf4"; ats_ok_border="#86efac"; ats_ok_color="#15803d"
    ats_warn_bg="#fffbeb"; ats_warn_border="#fcd34d"; ats_warn_color="#b45309"
    toggle_icon = "🌙"; toggle_label = "Dark Mode"
    upload_bg = "#f5f0ff"; upload_border = "#c4b5fd"
    browse_bg = "#ede9fe"; browse_color = "#6d28d9"; browse_border = "#c4b5fd"
    sidebar_btn_bg = "#ede9fe"; sidebar_btn_color = "#6d28d9"; sidebar_btn_border = "#c4b5fd"
    sidebar_btn_hover = "#ddd6fe"
    textarea_bg = "#fff5f0"; textarea_border = "#fed7aa"

# ---------- CSS ----------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
* {{ font-family: 'DM Sans', sans-serif; }}
h1, h2, h3 {{ font-family: 'Syne', sans-serif !important; }}
.stApp {{ background: {bg}; color: {text}; }}
[data-testid="stSidebar"] {{ background: {sidebar_bg} !important; border-right: 1px solid {border}; }}
[data-testid="stSidebar"] * {{ color: {sidebar_t} !important; }}
.hero-title {{ font-family:'Syne',sans-serif; font-size:3rem; font-weight:800;
    background:linear-gradient(135deg,#a78bfa,#60a5fa,#34d399);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    text-align:center; line-height:1.1; margin-bottom:0.25rem; }}
.hero-sub {{ text-align:center; color:{subtext}; font-size:1.05rem; margin-bottom:2rem; font-weight:300; }}
.card {{ background:{card_bg}; border:1px solid {border}; border-radius:16px; padding:24px; margin-bottom:16px; }}
.score-ring-container {{ display:flex; align-items:center; justify-content:center; flex-direction:column; padding:24px; }}
.score-number {{ font-family:'Syne',sans-serif; font-size:2rem; font-weight:800; line-height:1; }}
.score-label {{ font-size:0.85rem; color:{subtext}; margin-top:4px; letter-spacing:0.1em; text-transform:uppercase; }}
.cat-bar-bg {{ background:{bar_bg}; border-radius:99px; height:8px; margin:6px 0 14px 0; overflow:hidden; }}
.cat-bar-fill {{ height:8px; border-radius:99px; }}
.chip {{ display:inline-block; border-radius:99px; padding:4px 14px; margin:4px; font-size:0.82rem; font-weight:500; }}
.chip-found   {{ background:{chip_found_bg};   color:{chip_found_color};   border:1px solid {chip_found_border}; }}
.chip-missing {{ background:{chip_missing_bg}; color:{chip_missing_color}; border:1px solid {chip_missing_border}; }}
.chip-cat     {{ background:{chip_cat_bg};     color:{chip_cat_color};     border:1px solid {chip_cat_border}; }}
.chip-tool    {{ background:{chip_tool_bg};    color:{chip_tool_color};    border:1px solid {chip_tool_border}; }}
.chip-soft    {{ background:{chip_soft_bg};    color:{chip_soft_color};    border:1px solid {chip_soft_border}; }}
.suggestion-card {{ background:{suggestion_bg}; border-left:3px solid {suggestion_border};
    border-radius:0 12px 12px 0; padding:14px 18px; margin-bottom:10px; font-size:0.95rem; color:{suggestion_text}; }}
.rewrite-card {{ background:{suggestion_bg}; border:1px solid {suggestion_border};
    border-radius:12px; padding:14px 18px; margin-bottom:10px; font-size:0.9rem; color:{suggestion_text}; }}
.section-header {{ font-family:'Syne',sans-serif; font-size:1.15rem; font-weight:700; color:{text};
    margin-bottom:14px; display:flex; align-items:center; gap:8px; }}
.preview-box {{ background:{preview_bg}; border:1px solid {border}; border-radius:12px; padding:16px;
    font-size:0.82rem; color:{subtext}; white-space:pre-wrap; max-height:200px; overflow-y:auto; line-height:1.6; }}
.cover-letter-box {{ background:{preview_bg}; border:1px solid {border}; border-radius:12px; padding:20px;
    font-size:0.9rem; color:{text}; white-space:pre-wrap; line-height:1.8; max-height:400px; overflow-y:auto; }}
.history-card {{ background:{card_bg}; border:1px solid {border}; border-radius:12px;
    padding:12px 16px; margin-bottom:8px; }}
.job-title-badge {{ display:inline-block;
    background:linear-gradient(135deg,rgba(124,58,237,0.12),rgba(37,99,235,0.12));
    border:1px solid rgba(124,58,237,0.35); color:#a78bfa;
    border-radius:99px; padding:5px 18px; font-size:0.88rem; font-weight:600; margin-bottom:14px; }}
.score-guide-item {{ display:flex; align-items:center; gap:8px; font-size:0.85rem; padding:4px 0; }}
.dot {{ width:10px; height:10px; border-radius:50%; flex-shrink:0; }}
[data-testid="stFileUploader"] {{ background:{upload_bg} !important; border:2px dashed {upload_border} !important; border-radius:14px !important; }}
[data-testid="stFileUploader"] > div {{ background:{upload_bg} !important; border-radius:12px !important; }}
[data-testid="stFileUploader"] section {{ background:{upload_bg} !important; border:none !important; border-radius:12px !important; }}
[data-testid="stFileUploader"] section > div {{ background:{upload_bg} !important; }}
[data-testid="stFileUploaderDropzone"] {{ background:{upload_bg} !important; border:2px dashed {upload_border} !important; border-radius:12px !important; }}
[data-testid="stFileUploaderDropzone"] * {{ color:{text} !important; }}
[data-testid="stFileUploaderDropzone"] button {{ background:{browse_bg} !important; color:{browse_color} !important; border:1px solid {browse_border} !important; border-radius:8px !important; }}
[data-testid="stFileUploader"] span, [data-testid="stFileUploader"] small, [data-testid="stFileUploader"] p {{ color:{text} !important; }}
textarea {{ background-color:{textarea_bg} !important; border:1px solid {textarea_border} !important; color:{input_text} !important; border-radius:10px !important; }}
[data-testid="stTextArea"] > div > div {{ background-color:{textarea_bg} !important; border-radius:10px !important; }}
.stButton>button {{ background:linear-gradient(135deg,#7c3aed,#2563eb); color:white; border-radius:10px;
    height:3em; font-size:16px; border:none; font-family:'Syne',sans-serif; font-weight:600; width:100%; transition:opacity 0.2s; }}
.stButton>button:hover {{ opacity:0.85; }}
[data-testid="stSidebar"] .stButton>button {{ background:{sidebar_btn_bg} !important; color:{sidebar_btn_color} !important;
    border:1px solid {sidebar_btn_border} !important; border-radius:99px !important; font-size:0.82rem !important;
    font-family:'Syne',sans-serif !important; font-weight:600 !important; height:2.4em !important;
    width:100% !important; box-shadow:none !important; }}
[data-testid="stSidebar"] .stButton>button:hover {{ background:{sidebar_btn_hover} !important; opacity:1 !important; }}
[data-testid="stDownloadButton"] button {{ background:linear-gradient(135deg,#7c3aed,#2563eb) !important;
    color:white !important; border:none !important; border-radius:10px !important;
    font-family:'Syne',sans-serif !important; font-weight:600 !important; font-size:15px !important;
    height:3em !important; box-shadow:0 2px 12px rgba(124,58,237,0.3) !important; }}
hr {{ border-color:{border} !important; }}
#confetti-canvas {{ position:fixed; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:9999; }}
</style>
""", unsafe_allow_html=True)


# ---------- HELPERS ----------
def score_color(s):
    return "#34d399" if s >= 70 else "#fbbf24" if s >= 40 else "#f87171"

def score_label(s):
    return "Strong Match ✅" if s >= 70 else "Moderate Match ⚡" if s >= 40 else "Weak Match ❌"

def check_resume_strength(text):
    issues = []; score = 100
    wc = len(text.split())
    if wc < 200: issues.append("Resume seems too short (less than 200 words)"); score -= 20
    elif wc > 1000: issues.append("Resume may be too long (over 1000 words)"); score -= 10
    verbs = ["developed","built","led","managed","designed","created","implemented",
             "improved","achieved","delivered","launched","increased","reduced"]
    if len([v for v in verbs if v in text.lower()]) < 3:
        issues.append("Few action verbs — use words like 'built', 'led', 'delivered'"); score -= 20
    if not re.search(r'\d+', text):
        issues.append("No numbers found — quantify achievements (e.g., '30% faster')"); score -= 20
    return max(score, 0), issues

def check_ats(text):
    w = []
    if len(text) < 100: w.append("Very little text extracted — resume may use images or complex formatting")
    if re.search(r'[│┤╡╢╖╕╣║╗╝╔╩╦╠═╬]', text): w.append("Special box characters detected — may break ATS parsing")
    return w

def category_scores(resume_text, jd, overall_score):
    cats = {
        "Skills & Tech": ["python","javascript","sql","react","aws","docker","api","machine learning","data","cloud","java","git"],
        "Experience":    ["experience","years","worked","developed","built","led","managed","delivered"],
        "Education":     ["bachelor","master","degree","university","college","certification","certified"],
    }
    jl = jd.lower(); rl = resume_text.lower(); results = {}
    for cat, kws in cats.items():
        hits = [k for k in kws if k in jl]
        if not hits: results[cat] = None; continue
        raw = round(len([k for k in hits if k in rl]) / len(hits) * 100)
        # Scale relative to overall score to keep consistent
        results[cat] = min(raw, overall_score + 20)
    return results

def get_found_keywords(resume_text, jd):
    words = set(re.findall(r'\b[a-zA-Z]{3,}\b', jd.lower()))
    stops = {"the","and","for","with","that","this","are","you","will","have","has",
             "from","your","our","not","but","can","all","was","they","their","also","any","its"}
    rl = resume_text.lower()
    return sorted([w for w in words if w in rl and w not in stops])

def detect_job_title(jd):
    jl = jd.lower()
    roles = {
        "Data Analyst":       ["data analyst","sql","excel","tableau","power bi","data analysis"],
        "Data Scientist":     ["data scientist","machine learning","python","scikit","tensorflow","model"],
        "Software Engineer":  ["software engineer","developer","backend","frontend","api","rest","git"],
        "Frontend Developer": ["frontend","react","vue","css","html","javascript","ui"],
        "Backend Developer":  ["backend","node","django","flask","api","server","database"],
        "Product Manager":    ["product manager","roadmap","stakeholder","user story","agile","sprint"],
        "UX Designer":        ["ux","user experience","figma","wireframe","prototype","design"],
        "DevOps Engineer":    ["devops","ci/cd","docker","kubernetes","jenkins","pipeline","cloud"],
        "Data Engineer":      ["data engineer","etl","pipeline","spark","kafka","airflow","warehouse"],
        "Marketing Manager":  ["marketing","campaign","seo","content","brand","social media"],
    }
    best, best_n = "General Role", 0
    for role, kws in roles.items():
        n = sum(1 for k in kws if k in jl)
        if n > best_n: best, best_n = role, n
    return best

def categorize_missing(missing_keywords):
    technical = {"python","java","javascript","sql","r","scala","typescript","c++","go","rust",
                 "machine learning","deep learning","nlp","data analysis","statistics","algorithms"}
    tools = {"docker","kubernetes","aws","azure","gcp","git","github","jenkins","terraform",
             "react","node","django","flask","spark","kafka","airflow","tableau","excel","figma","jira"}
    soft = {"communication","leadership","teamwork","collaboration","problem solving","analytical",
            "critical thinking","creativity","adaptability","management","presentation"}
    cats = {"Technical Skills": [], "Tools & Platforms": [], "Soft Skills": [], "Other": []}
    for kw in missing_keywords:
        kl = kw.lower()
        if kl in technical: cats["Technical Skills"].append(kw)
        elif kl in tools: cats["Tools & Platforms"].append(kw)
        elif kl in soft: cats["Soft Skills"].append(kw)
        else: cats["Other"].append(kw)
    return {k: v for k, v in cats.items() if v}

def call_claude(prompt):
    try:
        api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            return None
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )
        data = resp.json()
        return data["content"][0]["text"] if data.get("content") else None
    except Exception:
        return None

def generate_report(score, cat_scores, missing_cats, suggestions, ats_warnings, strength_score, job_title, cover_letter):
    lines = [
        "AI RESUME SCANNER — ANALYSIS REPORT",
        "=" * 40,
        f"Detected Role:       {job_title}",
        f"Overall Match Score: {score}%  ({score_label(score)})",
        f"Resume Strength:     {strength_score}%",
        "", "CATEGORY BREAKDOWN", "-" * 30,
    ]
    for cat, val in cat_scores.items():
        if val is not None: lines.append(f"  {cat}: {val}%")
    lines += ["", "MISSING KEYWORDS BY CATEGORY", "-" * 30]
    if missing_cats:
        for cat_name, kws in missing_cats.items():
            lines.append(f"\n  [{cat_name}]")
            for kw in kws: lines.append(f"    - {kw}")
    else:
        lines.append("  None — all keywords found!")
    lines += ["", "IMPROVEMENT SUGGESTIONS", "-" * 30]
    for s in suggestions: lines.append(f"  • {s}")
    if ats_warnings:
        lines += ["", "ATS WARNINGS", "-" * 30]
        for w in ats_warnings: lines.append(f"  - {w}")
    if cover_letter:
        lines += ["", "COVER LETTER", "-" * 30, cover_letter]
    lines += ["", "=" * 40, "Generated by AI Resume Scanner"]
    return "\n".join(lines)


# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("### ⚙️ Settings & Tips")
    st.button(f"{toggle_icon}  {toggle_label}", on_click=toggle_theme, key="theme_toggle")
    st.divider()
    st.markdown("**How to get a better score:**")
    st.markdown("- Mirror keywords from the job description\n- Quantify your achievements\n- Use action verbs\n- Keep formatting ATS-friendly")
    st.divider()
    st.markdown("**Score Guide**")
    st.markdown(f"""
<div>
  <div class='score-guide-item'><div class='dot' style='background:#34d399'></div><span style='color:{subtext}'>70%+ &rarr; Strong Match</span></div>
  <div class='score-guide-item'><div class='dot' style='background:#fbbf24'></div><span style='color:{subtext}'>40-69% &rarr; Moderate</span></div>
  <div class='score-guide-item'><div class='dot' style='background:#f87171'></div><span style='color:{subtext}'>&lt;40% &rarr; Needs Work</span></div>
</div>
""", unsafe_allow_html=True)
    st.divider()

    if st.session_state.history:
        st.markdown("**📋 Match History**")
        for h in reversed(st.session_state.history[-5:]):
            c = score_color(h['score'])
            st.markdown(f"""
<div class='history-card'>
  <div style='font-size:0.8rem;color:{subtext};margin-bottom:2px'>{h['file']}</div>
  <div style='display:flex;justify-content:space-between;align-items:center'>
    <span style='font-size:0.75rem;color:{subtext}'>{h['role']}</span>
    <span style='font-size:1.1rem;font-weight:700;color:{c}'>{h['score']}%</span>
  </div>
</div>""", unsafe_allow_html=True)
        if st.button("🗑 Clear History", key="clear_hist"):
            st.session_state.history = []
            st.rerun()

    st.caption("Built with Streamlit · TF-IDF & NLP")


# ---------- HERO ----------
st.markdown("<div class='hero-title'>📄 AI Resume Scanner</div>", unsafe_allow_html=True)
st.markdown(f"<p class='hero-sub'>Check how well your resume matches any job description — instantly</p>", unsafe_allow_html=True)
st.divider()

# ---------- INPUTS ----------
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("<div class='section-header'>📎 Upload Resume</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload PDF or DOCX", type=["pdf","docx"], label_visibility="collapsed")

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
        if uploaded_file.name.endswith(".pdf"):
            resume_text = extract_text_from_pdf(uploaded_file)
        else:
            resume_text = extract_text_from_docx(uploaded_file)

        score, missing_keywords = keyword_match(resume_text, job_description)
        suggestions = generate_suggestions(missing_keywords)
        cat_scores = category_scores(resume_text, job_description, score)
        found_keywords = get_found_keywords(resume_text, job_description)
        missing_cats = categorize_missing(missing_keywords)
        strength_score, strength_issues = check_resume_strength(resume_text)
        ats_warnings = check_ats(resume_text)
        job_title = detect_job_title(job_description)

        st.session_state.history.append({"file": uploaded_file.name, "score": score, "role": job_title})
        st.session_state.cover_letter = None
        st.session_state.rewrite_bullets = None

    # Confetti for high scores
    if score >= 80:
        st.markdown("""
        <canvas id="confetti-canvas"></canvas>
        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
        <script>
        var canvas = document.getElementById('confetti-canvas');
        var myConfetti = confetti.create(canvas, {{ resize: true }});
        myConfetti({{ particleCount: 150, spread: 80, origin: {{ y: 0.4 }},
            colors: ['#a78bfa','#60a5fa','#34d399','#fbbf24','#f87171'] }});
        </script>
        """, unsafe_allow_html=True)
        st.balloons()

    st.divider()

    # Job Title Badge
    st.markdown(f"<div class='job-title-badge'>🎯 Detected Role: {job_title}</div>", unsafe_allow_html=True)

    # ROW 1: Score + Breakdown
    col_score, col_cats = st.columns([1, 2], gap="large")

    with col_score:
        sc = score_color(score)
        st.markdown(f"""
        <div class='card score-ring-container'>
            <div class='score-number' style='color:{sc}'>{score}%</div>
            <div class='score-label'>Match Score</div>
            <div style='margin-top:10px;font-size:0.9rem;color:#9ca3af'>{score_label(score)}</div>
        </div>""", unsafe_allow_html=True)

        s_color = score_color(strength_score)
        st.markdown(f"""
        <div class='card'>
            <div class='section-header'>💪 Resume Strength</div>
            <div style='font-size:2rem;font-weight:800;color:{s_color};font-family:Syne,sans-serif'>{strength_score}%</div>
            <div class='cat-bar-bg'><div class='cat-bar-fill' style='width:{strength_score}%;background:{s_color}'></div></div>
        </div>""", unsafe_allow_html=True)
        for issue in strength_issues:
            st.markdown(f"<div style='background:{ats_warn_bg};border:1px solid {ats_warn_border};border-radius:10px;padding:10px 14px;color:{ats_warn_color};margin-bottom:8px;font-size:0.88rem'>⚠ {issue}</div>", unsafe_allow_html=True)

    with col_cats:
        st.markdown("<div class='section-header'>📊 Score Breakdown</div>", unsafe_allow_html=True)
        for cat, val in cat_scores.items():
            if val is None: continue
            c = score_color(val)
            st.markdown(f"""<div style='margin-bottom:6px'>
                <div style='display:flex;justify-content:space-between;font-size:0.9rem;color:{subtext}'>
                    <span>{cat}</span><span style='color:{c};font-weight:600'>{val}%</span>
                </div>
                <div class='cat-bar-bg'><div class='cat-bar-fill' style='width:{val}%;background:{c}'></div></div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div class='section-header' style='margin-top:20px'>🤖 ATS Compatibility</div>", unsafe_allow_html=True)
        if ats_warnings:
            for w in ats_warnings:
                st.markdown(f"<div style='background:{ats_warn_bg};border:1px solid {ats_warn_border};border-radius:10px;padding:12px 16px;color:{ats_warn_color};margin-bottom:8px;font-size:0.9rem'>⚠ {w}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background:{ats_ok_bg};border:1px solid {ats_ok_border};border-radius:10px;padding:12px 16px;color:{ats_ok_color};font-size:0.9rem'>✓ No ATS issues detected!</div>", unsafe_allow_html=True)

    st.divider()

    # Resume Preview
    with st.expander("👁️ Resume Text Preview — verify it parsed correctly"):
        st.markdown(f"<div class='preview-box'>{resume_text[:2000]}{'...' if len(resume_text) > 2000 else ''}</div>", unsafe_allow_html=True)

    st.divider()

    # Keywords
    col_found, col_missing = st.columns(2, gap="large")

    with col_found:
        st.markdown(f"<div class='section-header'>✅ Found Keywords ({len(found_keywords)})</div>", unsafe_allow_html=True)
        if found_keywords:
            st.markdown(" ".join([f"<span class='chip chip-found'>{k}</span>" for k in found_keywords[:25]]), unsafe_allow_html=True)
        else:
            st.caption("No matching keywords found.")

    with col_missing:
        st.markdown("<div class='section-header'>🚨 Missing by Category</div>", unsafe_allow_html=True)
        cat_styles = {"Technical Skills":"chip-cat","Tools & Platforms":"chip-tool","Soft Skills":"chip-soft","Other":"chip-missing"}
        if missing_cats:
            for cat_name, kws in missing_cats.items():
                style = cat_styles.get(cat_name, "chip-missing")
                st.markdown(f"<div style='font-size:0.78rem;color:{subtext};margin:8px 0 4px;text-transform:uppercase;letter-spacing:0.06em'>{cat_name}</div>", unsafe_allow_html=True)
                st.markdown(" ".join([f"<span class='chip {style}'>{k}</span>" for k in kws]), unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background:{ats_ok_bg};border:1px solid {ats_ok_border};border-radius:10px;padding:12px 16px;color:{ats_ok_color};font-size:0.9rem'>✓ All keywords found!</div>", unsafe_allow_html=True)

    st.divider()

    # AI Features - Rewrite Suggestions only
    st.markdown("<div class='section-header'>✍️ Resume Rewrite Suggestions</div>", unsafe_allow_html=True)
    if missing_keywords:
        if st.session_state.rewrite_bullets is None:
            with st.spinner("Generating bullet point suggestions..."):
                st.session_state.rewrite_bullets = call_claude(f"""You are a professional resume writer.
The candidate is applying for a {job_title} role.
Their resume is missing these keywords: {', '.join(missing_keywords[:8])}.
Write 3 strong resume bullet points they could add to include these missing skills.
Each bullet starts with an action verb and includes a metric where possible.
Format: just 3 bullet points, one per line, starting with •""")
        if st.session_state.rewrite_bullets:
            for line in st.session_state.rewrite_bullets.strip().split("\n"):
                if line.strip():
                    st.markdown(f"<div class='rewrite-card'>{line.strip()}</div>", unsafe_allow_html=True)
        else:
            for s in suggestions[:3]:
                st.markdown(f"<div class='suggestion-card'>💡 {s}</div>", unsafe_allow_html=True)
    else:
        st.success("✅ No missing keywords — your resume looks great!")

    st.divider()

    # Suggestions
    st.markdown("<div class='section-header'>✨ Improvement Suggestions</div>", unsafe_allow_html=True)
    for s in suggestions:
        st.markdown(f"<div class='suggestion-card'>💡 {s}</div>", unsafe_allow_html=True)

    st.divider()

    report_text = generate_report(score, cat_scores, missing_cats, suggestions,
                                  ats_warnings, strength_score, job_title, st.session_state.cover_letter)
    st.download_button("📥 Download Full Report", data=report_text,
                       file_name="resume_analysis_report.txt", mime="text/plain", key="dl_report")

elif not uploaded_file or not job_description:
    st.markdown(f"""
    <div style='text-align:center;color:{subtext};padding:40px 0;font-size:1rem'>
        Upload your resume <strong style='color:#a78bfa'>(PDF or DOCX)</strong> and paste a job description above,
        then click <strong style='color:#a78bfa'>Analyze Resume</strong>
    </div>""", unsafe_allow_html=True)

st.divider()
st.markdown(f"<div style='text-align:center;color:{subtext};font-size:0.8rem'>AI Resume Scanner · Built with Streamlit & NLP</div>", unsafe_allow_html=True)