import sys
from pathlib import Path

# The modules in src/ import each other by name (python src/parser.py style).
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

from classifier import evaluate_resume_profile
from extractor import extract_resume_entities, save_extracted_data
from normalizer import normalize_qualifications
from profiles import PROFILES

# 1. Page Configuration (Following Streamlit Guide structure)
st.set_page_config(
    page_title="ResumeLens - Automata & Transducer Resume Validator",
    page_icon="📄",
    layout="wide"
)

st.title("📄 ResumeLens: Formal Resume Validator & Analyzer")
st.markdown(
    "A formal language tool that extracts candidate entities, normalizes skills "
    "using a **Finite-State Transducer (FST)**, and classifies professional profiles "
    "using **Deterministic Finite Automata (DFA)** built with `pyformlang`."
)

# 2. Sidebar for Inputs (Similar to the input widgets pattern in the guide)
st.sidebar.header("Candidate Input Options")
input_method = st.sidebar.radio("Choose input method:", ("Paste Resume Text", "Upload Text File"))

resume_text = ""

if input_method == "Paste Resume Text":
    resume_text = st.sidebar.text_area(
        "Paste resume plaintext here:",
        value="Juan Perez\njuan.perez@email.com\nPhone: +57 3101234567\n"
              "3 years of experience.\nEducation: Bachelor in Systems Engineering.\n"
              "Skills: Javascript, React, Node.js, PostgreSQL, Git",
        height=220
    )
else:
    uploaded_file = st.sidebar.file_uploader("Upload resume file (.txt)", type=["txt"])
    if uploaded_file is not None:
        resume_text = uploaded_file.read().decode("utf-8")

target_profile = st.sidebar.selectbox("Target Professional Profile", PROFILES)

if st.sidebar.button("Run Pipeline"):
    if not resume_text.strip():
        st.warning("Please provide valid text or upload a resume file.")
    else:
        # Step 1: Extraction
        extracted_data = extract_resume_entities(resume_text)
        save_extracted_data(extracted_data, output_path="outputs/extracted_resume.json")

        # Step 2: Normalization via FST
        raw_techs = extracted_data.get("technologies", [])
        normalized_techs = normalize_qualifications(raw_techs, target_profile)

        # Step 3: Classification via DFA
        is_accepted = evaluate_resume_profile(normalized_techs, target_profile)

        # Save to session state
        st.session_state["extracted_data"] = extracted_data
        st.session_state["normalized_techs"] = normalized_techs
        st.session_state["is_accepted"] = is_accepted
        st.session_state["target_profile"] = target_profile
        st.success("Pipeline executed successfully!")

# 3. Display Results using Tabs (Following st.tabs pattern from Step 9 & 20 of the guide)
if "extracted_data" in st.session_state:
    tab1, tab2, tab3 = st.tabs([
        "📋 Extracted Entities",
        "🔄 FST Normalization",
        "🤖 DFA Profile Evaluation"
    ])

    with tab1:
        st.subheader("Structured Resume Information")
        data = st.session_state["extracted_data"]

        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Candidate Name", value=data.get("name", "Unknown"))
            st.metric(label="Email", value=data.get("email", "Unknown"))
        with col2:
            st.metric(label="Phone", value=data.get("phone", "Unknown"))
            st.metric(label="Years of Experience", value=data.get("experience_years", "0"))

        st.markdown("**Education Background:**")
        st.write(", ".join(data.get("education", [])) if data.get("education") else "None detected")

        st.markdown("**Raw Extracted Technologies:**")
        st.write(data.get("technologies", []))

    with tab2:
        st.subheader("Finite-State Transducer (FST) Output")
        st.markdown("Mapped variants to canonical forms and sorted by professional hierarchy:")
        st.write(st.session_state["normalized_techs"])

    with tab3:
        st.subheader("Deterministic Finite Automaton (DFA) Verdict")
        accepted = st.session_state["is_accepted"]
        prof = st.session_state["target_profile"]

        if accepted:
            st.success(f"✅ The candidate **PASSES** the sequence validation for the **{prof}** profile!")
            st.balloons()
        else:
            st.error(f"❌ The candidate **REJECTED** for the **{prof}** profile criteria.")

        st.markdown(f"**Evaluated Canonical Sequence:** `{' -> '.join(st.session_state['normalized_techs']) if st.session_state['normalized_techs'] else 'Empty'}`")
else:
    st.info("👈 Use the sidebar to input your resume details and click **Run Pipeline**.")