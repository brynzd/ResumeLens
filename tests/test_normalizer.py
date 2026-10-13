"""Stage 2: normalization with the finite-state transducer and canonical order."""

import pytest

from extractor import extract_resume_entities
from normalizer import normalize, sort_for_profile, translate

# Transformations of the assignment (Integrative Task 1, stage 2)
ASSIGNMENT_TABLE = [
    ("JS", "JAVASCRIPT"), ("Javascript", "JAVASCRIPT"),
    ("React.js", "REACT"), ("ReactJS", "REACT"),
    ("NodeJS", "NODE_JS"), ("Node.js", "NODE_JS"),
    ("Postgres", "POSTGRESQL"), ("PostgreSQL", "POSTGRESQL"),
    ("pandas", "PANDAS"),
    ("sklearn", "SCIKIT_LEARN"), ("scikit learn", "SCIKIT_LEARN"), ("Scikit-learn", "SCIKIT_LEARN"),
    ("Tensor Flow", "TENSORFLOW"), ("TensorFlow", "TENSORFLOW"),
    ("Py Torch", "PYTORCH"), ("PyTorch", "PYTORCH"),
]

# Some of the team's own transformations
TEAM_TABLE = [
    ("TypeScript", "TYPESCRIPT"), ("Vue.js", "VUE"), ("Tailwind CSS", "TAILWIND"),
    ("Spring Boot", "SPRING_BOOT"), ("NumPy", "NUMPY"), ("Apache Spark", "SPARK"),
    ("Mongo DB", "MONGODB"), ("Python3", "PYTHON"),
]


@pytest.mark.parametrize("written, token", ASSIGNMENT_TABLE)
def test_transformations_of_the_assignment(written, token):
    # Stage 1 extracts the spelling as one string and the transducer translates it
    extracted = extract_resume_entities(f"Technical Skills: {written}.")["technologies"]
    assert extracted == [written]
    assert translate(written) == token


@pytest.mark.parametrize("written, token", TEAM_TABLE)
def test_transformations_of_the_team(written, token):
    assert translate(written) == token


def test_unknown_strings_are_reported():
    tokens, unknown = normalize(["Git", "COBOL", "Docker"])
    assert tokens == ["GIT"]
    assert unknown == ["COBOL", "Docker"]


def test_equivalent_spellings_give_one_token():
    tokens, unknown = normalize(["JS", "Javascript", "JavaScript", "React.js", "ReactJS"])
    assert tokens == ["JAVASCRIPT", "REACT"]
    assert unknown == []


def test_canonical_order_of_the_assignment():
    # Git, NodeJS, JS, Postgres, React.js -> JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT
    tokens, _ = normalize(["Git", "NodeJS", "JS", "Postgres", "React.js"])
    assert sort_for_profile(tokens, "FULL_STACK_DEVELOPER") == [
        "JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT",
    ]


def test_each_profile_keeps_only_its_tokens():
    tokens, _ = normalize(["Python", "Pandas", "React", "Git"])
    assert sort_for_profile(tokens, "MACHINE_LEARNING_ENGINEER") == ["PYTHON", "PANDAS", "GIT"]
    assert sort_for_profile(tokens, "FRONTEND_DEVELOPER") == ["REACT", "GIT"]
