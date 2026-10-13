"""Stage 3 tests: qualification pattern recognition with one DFA per profile."""

import pytest

from classifier import create_profile_dfa, evaluate_resume_profile
from extractor import extract_resume_entities
from normalizer import normalize_qualifications
from profiles import PROFILES

WEDNESDAY = """Wednesday Addams
3 years of experience developing web applications.
Technical Skills:
JS, React.js, NodeJS, Postgres, Git."""

MARY_JANE = """Mary Jane Watson
 2 years of experience developing predictive models and data-processing pipelines.
Technical Skills:
 Python, Pandas, NumPy, Scikit-learn, TensorFlow, SQL, Git."""


def accepted_profiles(text):
    raw = extract_resume_entities(text)["technologies"]
    return [p for p in PROFILES if evaluate_resume_profile(normalize_qualifications(raw, p), p)]


def test_stage3_example_of_the_assignment():
    sequence = ["PYTHON", "PANDAS", "TENSORFLOW", "POSTGRESQL", "GIT"]
    assert evaluate_resume_profile(sequence, "MACHINE_LEARNING_ENGINEER")


def test_stage3_example_written_as_a_resume():
    # Same qualifications, through stages 1 and 2 first.
    text = "Technical Skills: Python, Pandas, TensorFlow, Postgres, Git."
    assert accepted_profiles(text) == ["MACHINE_LEARNING_ENGINEER"]


@pytest.mark.parametrize("text, profile", [
    (WEDNESDAY, "FULL_STACK_DEVELOPER"),
    (MARY_JANE, "MACHINE_LEARNING_ENGINEER"),
])
def test_reference_fragments_satisfy_only_their_profile(text, profile):
    assert accepted_profiles(text) == [profile]


@pytest.mark.parametrize("profile, sequence, expected", [
    # Full Stack: language -> frontend -> backend -> database -> version control
    ("FULL_STACK_DEVELOPER", ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"], True),
    ("FULL_STACK_DEVELOPER", ["TYPESCRIPT", "ANGULAR", "DJANGO", "MONGODB", "GIT"], True),
    ("FULL_STACK_DEVELOPER", ["JAVASCRIPT", "REACT", "NODE_JS", "SQL", "GIT"], True),  # SQL database
    ("FULL_STACK_DEVELOPER", ["JAVASCRIPT", "TYPESCRIPT", "REACT", "VUE", "NODE_JS", "DJANGO",
                              "POSTGRESQL", "MONGODB", "SQL", "GIT"], True),           # extras
    ("FULL_STACK_DEVELOPER", ["JAVASCRIPT", "REACT", "POSTGRESQL", "GIT"], False),     # no backend
    ("FULL_STACK_DEVELOPER", ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL"], False),  # no Git
    # Machine Learning: Python -> data library -> ML framework -> database -> version control
    ("MACHINE_LEARNING_ENGINEER", ["PYTHON", "NUMPY", "PYTORCH", "SQL", "GIT"], True),
    ("MACHINE_LEARNING_ENGINEER", ["PYTHON", "PANDAS", "SQL", "GIT"], False),        # no framework
    # Frontend: language -> UI framework -> styling -> version control
    ("FRONTEND_DEVELOPER", ["TYPESCRIPT", "VUE", "TAILWIND", "GIT"], True),
    ("FRONTEND_DEVELOPER", ["JAVASCRIPT", "REACT", "GIT"], False),                   # no styling
    # Data Engineer: language -> pipeline technology -> database -> version control
    ("DATA_ENGINEER", ["PYTHON", "SPARK", "AIRFLOW", "POSTGRESQL", "GIT"], True),
    ("DATA_ENGINEER", ["SCALA", "SPARK", "SQL", "GIT"], True),
    ("DATA_ENGINEER", ["PYTHON", "SQL", "GIT"], False),                              # no pipeline
])
def test_profile_patterns(profile, sequence, expected):
    assert evaluate_resume_profile(sequence, profile) is expected


def test_full_stack_accepts_sql_through_the_whole_pipeline():
    text = "Technical Skills: JavaScript, React, Node.js, SQL, Git."
    assert "FULL_STACK_DEVELOPER" in accepted_profiles(text)


@pytest.mark.parametrize("sequence", [
    [],                                                       # empty
    ["REACT", "JAVASCRIPT", "NODE_JS", "POSTGRESQL", "GIT"],  # categories out of order
    ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT", "PYTHON"],  # symbol outside Σ
])
def test_sequences_the_full_stack_dfa_rejects(sequence):
    assert not evaluate_resume_profile(sequence, "FULL_STACK_DEVELOPER")


@pytest.mark.parametrize("profile, states, symbols", [
    ("FULL_STACK_DEVELOPER", 6, 12),
    ("MACHINE_LEARNING_ENGINEER", 6, 9),
    ("FRONTEND_DEVELOPER", 5, 8),
    ("DATA_ENGINEER", 5, 7),
])
def test_automata_are_deterministic_and_match_their_5_tuple(profile, states, symbols):
    dfa = create_profile_dfa(profile)
    assert dfa.is_deterministic()
    assert len(dfa.states) == states
    assert len(dfa.symbols) == symbols
    # every symbol advances once and loops once (docs/automata.md)
    assert dfa.get_number_transitions() == 2 * symbols
    assert [str(s) for s in dfa.final_states] == [f"q{states - 1}"]


def test_unknown_profile_is_an_error():
    with pytest.raises(ValueError):
        create_profile_dfa("DEVOPS_ENGINEER")
