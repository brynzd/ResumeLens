"""Web interface (Streamlit): the four stages of the pipeline on one résumé.

Usage:
    streamlit run src/app.py
"""

import streamlit as st 

from parser import PROJECT_ROOT 
from pipeline import run_pipeline
from profiles import PROFILE_NAMES, PROFILES
from validator import get_validating_metamodel

SAMPLES = PROJECT_ROOT / "data" / "resumes"
DEFAULT_TEXT = (
    "Juan Perez\njuan.perez@email.com\nPhone: +57 3101234567\n"
    "3 years of experience.\nEducation: Bachelor in Systems Engineering.\n"
    "Skills: Javascript, React, Node.js, PostgreSQL, Git"
)


@st.cache_resource
def metamodel():
    """The textX metamodel with the semantic checks, built only once."""
    return get_validating_metamodel()


def read_resume():
    """Text of the résumé chosen in the sidebar: a sample, pasted text or a file."""
    st.sidebar.header("Candidate Input Options")
    method = st.sidebar.radio(
        "Choose input method:", ("Sample Resume", "Paste Resume Text", "Upload Text File")
    )
    if method == "Sample Resume":
        samples = sorted(path.name for path in SAMPLES.glob("*.txt"))
        sample = st.sidebar.selectbox(
            "Sample résumé (data/resumes/)", samples, index=samples.index("wednesday.txt")
        )
        text = (SAMPLES / sample).read_text(encoding="utf-8")
        st.sidebar.text_area("Résumé text:", text, height=260, disabled=True)
        return text
    if method == "Paste Resume Text":
        return st.sidebar.text_area("Paste resume plaintext here:", value=DEFAULT_TEXT, height=260)
    uploaded = st.sidebar.file_uploader("Upload resume file (.txt)", type=["txt"])
    if uploaded is None:
        return ""
    return uploaded.read().decode("utf-8")


def show_extraction(data):
    st.subheader("Structured Resume Information")
    personal = data["personal"]
    contact = data["contact"]
    years = data["experience_years"]
    col1, col2, col3 = st.columns(3)
    col1.metric("Candidate Name", personal["name"] or "Unknown")
    col1.metric("Headline", personal["headline"] or "Unknown")
    col2.metric("Email", contact["email"] or "Unknown")
    col2.metric("Phone", contact["phone"] or "Unknown")
    col3.metric("Location", personal["location"] or "Unknown")
    col3.metric("Years of Experience", years if years is not None else "Unknown")
    if contact["linkedin"]:
        st.markdown(f"**LinkedIn:** {contact['linkedin']}")

    st.markdown("**Skills as written, by category:**")
    rows = []
    for category, found in data["skills"].items():
        rows.append({"Category": category.replace("_", " "), "Strings": ", ".join(found) or "-"})
    st.table(rows)

    languages = ", ".join(f"{lang['name']} ({lang['level']})" for lang in data["languages"])
    st.markdown(
        f"**Other qualifications:** {', '.join(data['other_qualifications']) or '-'}  \n"
        f"**Academic qualifications:** {', '.join(data['academic_qualifications']) or '-'}  \n"
        f"**Languages:** {languages or '-'}"
    )

    if data["experience"]:
        st.markdown("**Professional experience:**")
        rows = []
        for job in data["experience"]:
            rows.append({"Role": job["title"], "Company": job["organization"],
                         "Period": f"{job['start']} - {job['end']}", "Tasks": len(job["tasks"])})
        st.table(rows)
    if data["education"]:
        st.markdown("**Education:**")
        rows = []
        for degree in data["education"]:
            rows.append({"Degree": degree["title"], "Institution": degree["organization"],
                         "Period": f"{degree['start']} - {degree['end']}"})
        st.table(rows)
    with st.expander("Extracted data structure (JSON)"):
        st.json(data)


def show_normalization(result):
    st.subheader("Finite-State Transducer (FST) Output")
    st.markdown("Each string as written is one input symbol; the transducer writes its token:")
    rows = []
    for raw, token in result["translations"].items():
        rows.append({"Input (as written)": raw,
                     "Output (canonical token)": token or "no transition: unknown"})
    st.table(rows)
    st.markdown(
        f"**Canonical tokens (no duplicates):** `{', '.join(result['tokens']) or '-'}`  \n"
        f"**Unknown strings:** {', '.join(result['unknown']) or '-'}"
    )
    st.markdown("**Sorted by the canonical order of each profile** (the input of its automaton):")
    rows = []
    for profile in PROFILES:
        sequence = " -> ".join(result["sequences"][profile]) or "Empty"
        rows.append({"Profile": profile, "Canonical sequence": sequence})
    st.table(rows)


def show_recognition(result):
    st.subheader("Deterministic Finite Automaton (DFA) Verdicts")
    rows = []
    for profile in PROFILES:
        rows.append({
            "Profile": profile,
            "Evaluated Canonical Sequence": " -> ".join(result["sequences"][profile]) or "Empty",
            "Run (states)": " → ".join(result["traces"][profile]),
            "Verdict": "ACCEPTED" if result["verdicts"][profile] else "REJECTED",
        })
    st.table(rows)
    st.caption(
        "State qᵢ means the first i categories of the profile are covered. A run stops at the "
        "first symbol without a transition (implicit trap state) and is rejected."
    )


def show_document(result):
    st.subheader("Candidate Profile Document (ResumeLens DSL)")
    if result["missing"]:
        st.warning("The résumé does not provide: " + ", ".join(result["missing"]))
    st.code(result["document"], language=None)
    if result["error"]:
        st.error(f"textX rejected the document: {result['error']}")
    else:
        st.success("textX accepted the document (lexical, syntactic and semantic validation).")
        st.markdown("**Markdown visualization:**")
        with st.container(border=True):
            st.markdown(result["markdown"])


st.set_page_config(page_title="ResumeLens", page_icon="📄", layout="wide")
st.title("📄 ResumeLens: Formal Resume Validator & Analyzer")
st.markdown(
    "Extracts candidate information with **regular expressions**, normalizes skills with a "
    "**finite-state transducer**, recognizes the four profile patterns with **deterministic "
    "finite automata** (pyformlang) and validates the candidate document with a "
    "**context-free grammar** (textX)."
)

resume_text = read_resume()
if st.sidebar.button("Run Pipeline"):
    if resume_text.strip():
        st.session_state["result"] = run_pipeline(resume_text, metamodel())
    else:
        st.warning("Please provide valid text or upload a resume file.")

result = st.session_state.get("result")
if result is None:
    st.info("Use the sidebar to choose or write a résumé and click **Run Pipeline**.")
    st.stop()

accepted = [PROFILE_NAMES[profile] for profile in PROFILES if result["verdicts"][profile]]
if accepted:
    st.success("Accepted profiles: " + ", ".join(accepted))
else:
    st.error("No profile pattern is satisfied: the candidate is UNQUALIFIED.")

tab1, tab2, tab3, tab4 = st.tabs([
    "1. Extraction (regex)",
    "2. Normalization (FST)",
    "3. Recognition (DFA)",
    "4. Candidate document (textX)",
])
with tab1:
    show_extraction(result["extracted"])
with tab2:
    show_normalization(result)
with tab3:
    show_recognition(result)
with tab4:
    show_document(result)
