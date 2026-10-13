"""ResumeLens web UI (Streamlit): the four stages of the pipeline on one résumé.

Usage:
    streamlit run src/app.py
"""

import json
import sys
from pathlib import Path

# The modules in src/ import each other by name (python src/parser.py style).
sys.path.insert(0, str(Path(__file__).resolve().parent))

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
    """The textX metamodel with the semantic checks, built once."""
    return get_validating_metamodel()


def verdict(accepted):
    return "ACCEPTED" if accepted else "REJECTED"


# 1. Page Configuration
st.set_page_config(
    page_title="ResumeLens - Automata & Transducer Resume Validator",
    page_icon="📄",
    layout="wide"
)

st.title("📄 ResumeLens: Formal Resume Validator & Analyzer")
st.markdown(
    "A formal language tool that extracts candidate information with **regular expressions**, "
    "normalizes skills with a **Finite-State Transducer (FST)**, recognizes the four profile "
    "patterns with **Deterministic Finite Automata (DFA)** built with `pyformlang`, and validates "
    "the candidate document with a **context-free grammar** implemented in `textX`."
)

# 2. Sidebar for Inputs
st.sidebar.header("Candidate Input Options")
input_method = st.sidebar.radio(
    "Choose input method:", ("Sample Resume", "Paste Resume Text", "Upload Text File")
)

resume_text = ""
if input_method == "Sample Resume":
    samples = sorted(path.name for path in SAMPLES.glob("*.txt"))
    sample = st.sidebar.selectbox(
        "Sample résumé (data/resumes/)", samples, index=samples.index("wednesday.txt")
    )
    resume_text = (SAMPLES / sample).read_text(encoding="utf-8")
    st.sidebar.text_area("Résumé text:", resume_text, height=260, disabled=True)
elif input_method == "Paste Resume Text":
    resume_text = st.sidebar.text_area("Paste resume plaintext here:", value=DEFAULT_TEXT, height=260)
else:
    uploaded_file = st.sidebar.file_uploader("Upload resume file (.txt)", type=["txt"])
    if uploaded_file is not None:
        resume_text = uploaded_file.read().decode("utf-8")

if st.sidebar.button("Run Pipeline"):
    if not resume_text.strip():
        st.warning("Please provide valid text or upload a resume file.")
    else:
        st.session_state["result"] = run_pipeline(resume_text, metamodel())
        if any(st.session_state["result"]["verdicts"].values()):
            st.balloons()

# 3. Results of the four stages
result = st.session_state.get("result")
if result is None:
    st.info("👈 Use the sidebar to choose or write a résumé and click **Run Pipeline**.")
    st.stop()

data = result["extracted"]
accepted = [p for p in PROFILES if result["verdicts"][p]]
if accepted:
    st.success("Accepted profiles: " + ", ".join(PROFILE_NAMES[p] for p in accepted))
else:
    st.error("No profile pattern is satisfied: the candidate is UNQUALIFIED.")

tab1, tab2, tab3, tab4 = st.tabs([
    "📋 1 · Extraction (regex)",
    "🔄 2 · Normalization (FST)",
    "🤖 3 · Recognition (DFA)",
    "🧾 4 · Candidate document (textX)",
])

with tab1:
    st.subheader("Structured Resume Information")
    personal, contact = data["personal"], data["contact"]
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
    st.table([
        {"Category": category.replace("_", " "), "Strings": ", ".join(found) or "-"}
        for category, found in data["skills"].items()
    ])
    languages = ", ".join(f"{lang['name']} ({lang['level']})" for lang in data["languages"])
    st.markdown(
        f"**Other qualifications:** {', '.join(data['other_qualifications']) or '-'}  \n"
        f"**Academic qualifications:** {', '.join(data['academic_qualifications']) or '-'}  \n"
        f"**Languages:** {languages or '-'}"
    )
    if data["experience"]:
        st.markdown("**Professional experience:**")
        st.table([
            {"Role": e["title"], "Company": e["organization"], "Period": f"{e['start']} - {e['end']}",
             "Tasks": len(e["tasks"])}
            for e in data["experience"]
        ])
    if data["education"]:
        st.markdown("**Education:**")
        st.table([
            {"Degree": d["title"], "Institution": d["organization"], "Period": f"{d['start']} - {d['end']}"}
            for d in data["education"]
        ])
    with st.expander("Extracted data structure (JSON)"):
        st.json(data)
    st.download_button(
        "Download extracted_resume.json",
        json.dumps(data, indent=4, ensure_ascii=False),
        file_name="extracted_resume.json",
        mime="application/json",
    )

with tab2:
    st.subheader("Finite-State Transducer (FST) Output")
    st.markdown("Each string as written is one input symbol; the transducer writes its canonical token:")
    st.table([
        {"Input (as written)": raw, "Output (canonical token)": token or "no transition: unknown"}
        for raw, token in result["translations"].items()
    ])
    st.markdown(
        f"**Canonical tokens (no duplicates):** `{', '.join(result['tokens']) or '-'}`  \n"
        f"**Unknown strings:** {', '.join(result['unknown']) or '-'}"
    )
    st.markdown("**Sorted by the canonical order of each profile** (the input of its automaton):")
    st.table([
        {"Profile": profile, "Canonical sequence": " -> ".join(result["sequences"][profile]) or "Empty"}
        for profile in PROFILES
    ])

with tab3:
    st.subheader("Deterministic Finite Automaton (DFA) Verdicts")
    st.table([
        {
            "Profile": profile,
            "Evaluated Canonical Sequence": " -> ".join(result["sequences"][profile]) or "Empty",
            "Run (states)": " → ".join(result["traces"][profile]),
            "Verdict": verdict(result["verdicts"][profile]),
        }
        for profile in PROFILES
    ])
    for profile in PROFILES:
        if result["verdicts"][profile]:
            st.success(f"**{profile}**: ACCEPTED", icon="✅")
        else:
            st.error(f"**{profile}**: REJECTED", icon="❌")
    st.caption(
        "State qᵢ means the first i categories of the profile are covered. A run stops at the "
        "first symbol without a transition (implicit trap state) and is rejected."
    )

with tab4:
    st.subheader("Candidate Profile Document (ResumeLens DSL)")
    if result["missing"]:
        st.warning("The résumé does not provide: " + ", ".join(result["missing"]))
    st.code(result["document"], language=None)
    st.download_button("Download candidate.resume", result["document"], file_name="candidate.resume")
    if result["error"]:
        st.error(f"textX rejected the document: {result['error']}")
    else:
        st.success("textX accepted the document (lexical, syntactic and semantic validation).")
        st.markdown("**Markdown visualization:**")
        with st.container(border=True):
            st.markdown(result["markdown"])
        st.download_button("Download candidate.md", result["markdown"], file_name="candidate.md")
