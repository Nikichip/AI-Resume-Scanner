import streamlit as st
from utils import extract_text_from_pdf, keyword_match, generate_suggestions


st.set_page_config(
    page_title="AI Resume Scanner",
    page_icon="📄",
    layout="wide"
)

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>

/* App background */
.stApp {
    background-color: #f6f7fb;
}

/* Title */
h1 {
    text-align: center;
    color: #2c3e50;
    font-weight: 700;
}

/* Subtitle */
.subtitle {
    text-align: center;
    color: #6b7280;
    font-size: 17px;
}

/* Upload box */
[data-testid="stFileUploader"] {
    border: 2px dashed #c7d2fe;
    padding: 20px;
    border-radius: 12px;
    background-color: white;
}

/* Text area */
textarea {
    background-color: white !important;
    border-radius: 10px !important;
    border: 1px solid #d1d5db !important;
}

/* Button */
.stButton>button {
    background-color: #6366f1;
    color: white;
    border-radius: 10px;
    height: 3em;
    font-size: 16px;
    border: none;
}

.stButton>button:hover {
    background-color: #4f46e5;
}

/* Skill cards */
.skill-box {
    padding: 12px;
    border-radius: 8px;
    background-color: #fee2e2;
    margin-bottom: 8px;
    font-weight: 500;
}

/* Metric card */
[data-testid="stMetric"] {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.05);
}

</style>
""", unsafe_allow_html=True)

# ---------- TITLE ----------
st.markdown("<h1>📄 AI Resume Scanner</h1>", unsafe_allow_html=True)

st.markdown(
"<p class='subtitle'>Check how well your resume matches a job description using NLP</p>",
unsafe_allow_html=True
)

st.info("💡 Tip: Add keywords from the job description to improve your match score.")

st.divider()

# ---------- INPUT SECTION ----------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Upload Resume")
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

with col2:
    st.subheader("Paste Job Description")
    job_description = st.text_area("Paste job description here")

st.divider()

# ---------- ANALYSIS ----------
if uploaded_file and job_description:

    with st.spinner("Analyzing Resume..."):
        resume_text = extract_text_from_pdf(uploaded_file)
        score, missing_keywords = keyword_match(resume_text, job_description)

    st.subheader("📊 Match Score")

    col1, col2 = st.columns([1,2])

    with col1:
        st.metric("Resume Match Score", f"{score}%")

    with col2:
        st.progress(int(score))

    st.divider()

    # ---------- MISSING SKILLS ----------
    st.subheader("🚨 Missing Required Skills")

    if missing_keywords:
        for skill in missing_keywords:
            st.markdown(f"<div class='skill-box'>⚠️ {skill}</div>", unsafe_allow_html=True)
    else:
        st.success("✅ Your resume contains all required skills!")
    
    st.divider()
    
    st.subheader("✨ Resume Improvement Suggestions")
    
    suggestions = generate_suggestions(missing_keywords)
    for suggestion in suggestions:
        st.info(suggestion)


# ---------- FOOTER ----------
st.divider()
