import pdfplumber
from sklearn.feature_extraction.text import TfidfVectorizer
import re


def extract_text_from_pdf(file):
    text = ""

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""

    return text


def keyword_match(resume_text, job_description):

    # Important skill keywords to check
    skills = [
        "python", "machine learning", "sql", "data analysis",
        "git", "docker", "deep learning", "pandas", "numpy",
        "tensorflow", "pytorch", "api", "flask", "django"
    ]

    resume_text = resume_text.lower()

    missing_skills = []

    for skill in skills:
        if skill not in resume_text and skill in job_description.lower():
            missing_skills.append(skill)

    # TF-IDF score
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])

    score = (tfidf_matrix * tfidf_matrix.T).toarray()[0][1] * 100

    return round(score, 2), missing_skills

def generate_suggestions(missing_skills):
    
    suggestions = []

    if len(missing_skills) > 0:
        suggestions.append(
            "Consider adding the following skills if you have experience with them: "
            + ", ".join(missing_skills[:5])
        )

    suggestions.append(
        "Include a dedicated 'Skills' section in your resume to highlight technical tools."
    )

    suggestions.append(
        "Add project experience demonstrating the required technologies."
    )

    suggestions.append(
        "Use action verbs and measurable achievements (e.g., 'Improved model accuracy by 15%')."
    )

    suggestions.append(
        "Ensure important keywords from the job description appear naturally in your resume."
    )

    return suggestions