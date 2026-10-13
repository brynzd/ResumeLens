"""Stage 3: recognition of the profile patterns with one DFA per profile."""

import pytest

from classifier import classify, evaluate_resume_profile


def test_example_of_the_assignment():
    sequence = ["PYTHON", "PANDAS", "TENSORFLOW", "POSTGRESQL", "GIT"]
    assert evaluate_resume_profile(sequence, "MACHINE_LEARNING_ENGINEER")


@pytest.mark.parametrize("profile, sequence, accepted", [
    # Full Stack: language, frontend, backend, database, version control
    ("FULL_STACK_DEVELOPER", ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"], True),
    ("FULL_STACK_DEVELOPER", ["TYPESCRIPT", "ANGULAR", "DJANGO", "MONGODB", "GIT"], True),
    ("FULL_STACK_DEVELOPER", ["JAVASCRIPT", "REACT", "POSTGRESQL", "GIT"], False),  # no backend
    # Machine Learning: Python, data library, ML framework, database, version control
    ("MACHINE_LEARNING_ENGINEER",
     ["PYTHON", "PANDAS", "NUMPY", "SCIKIT_LEARN", "TENSORFLOW", "SQL", "GIT"], True),  # extras
    ("MACHINE_LEARNING_ENGINEER", ["PYTHON", "PANDAS", "SQL", "GIT"], False),  # no ML framework
    # Frontend: language, UI framework, styling, version control
    ("FRONTEND_DEVELOPER", ["TYPESCRIPT", "VUE", "TAILWIND", "GIT"], True),
    ("FRONTEND_DEVELOPER", ["JAVASCRIPT", "REACT", "GIT"], False),  # no styling
    # Data Engineer: language, pipeline technology, database, version control
    ("DATA_ENGINEER", ["PYTHON", "SPARK", "AIRFLOW", "POSTGRESQL", "GIT"], True),
    ("DATA_ENGINEER", ["PYTHON", "SQL", "GIT"], False),  # no pipeline technology
])
def test_profile_patterns(profile, sequence, accepted):
    assert evaluate_resume_profile(sequence, profile) == accepted


def test_several_profiles_can_accept_a_resume():
    tokens = ["JAVASCRIPT", "TYPESCRIPT", "VUE", "TAILWIND", "NODE_JS", "POSTGRESQL", "GIT"]
    assert classify(tokens) == {
        "FULL_STACK_DEVELOPER": True,
        "MACHINE_LEARNING_ENGINEER": False,
        "FRONTEND_DEVELOPER": True,
        "DATA_ENGINEER": False,
    }


def test_no_profile_accepts_an_unqualified_resume():
    assert not any(classify(["GIT"]).values())
