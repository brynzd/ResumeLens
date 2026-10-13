"""Stage 2 tests: normalization with the finite-state transducer and canonical order."""

import itertools

import pytest

from extractor import extract_resume_entities
from normalizer import (
    GLOBAL_ORDER, NORMALIZATION_FST, VARIANTS, normalize, normalize_qualifications,
    sort_for_profile, translate,
)
from profiles import PROFILES
from validator import CANONICAL_SKILLS

# Transformation table of the assignment (Integrative Task 1, stage 2).
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


@pytest.mark.parametrize("raw, token", ASSIGNMENT_TABLE)
def test_transformations_of_the_assignment(raw, token):
    assert translate(raw) == token


@pytest.mark.parametrize("raw, token", ASSIGNMENT_TABLE)
def test_assignment_spellings_go_through_stages_1_and_2(raw, token):
    extracted = extract_resume_entities(f"Technical Skills: {raw}.")["technologies"]
    assert [translate(s) for s in extracted] == [token]


@pytest.mark.parametrize(
    "spelling, token",
    [(spelling, token) for token, spellings in VARIANTS.items() for spelling in spellings],
)
def test_every_input_symbol_can_be_extracted(spelling, token):
    # Each symbol of Σ is a string stage 1 can produce, so no transition is dead.
    for written in (spelling, spelling.title(), spelling.upper()):
        extracted = extract_resume_entities(f"Technical Skills: {written}.")["technologies"]
        assert extracted == [written]
        assert translate(written) == token


@pytest.mark.parametrize("raw", [
    "Java Script", "Type Script", "Python3", "CSS3", "React JS", "Angular.js", "Vue JS",
    "Node JS", "SpringBoot", "Spring-Boot", "TailwindCSS", "Num Py", "ScikitLearn",
    "Mongo DB", "PySpark", "Apache Airflow", "Tensor\tFlow",
])
def test_other_extracted_spellings_are_known(raw):
    extracted = extract_resume_entities(f"Technical Skills: {raw}.")["technologies"]
    assert extracted == [raw]
    assert translate(raw) is not None


@pytest.mark.parametrize("raw", ["COBOL", "Docker", "Reac", "Reactt", "postgre", "React Native"])
def test_unknown_strings_are_rejected_by_the_transducer(raw):
    assert translate(raw) is None


def test_unknown_strings_are_reported_not_guessed():
    tokens, unknown = normalize(["Git", "COBOL", "Docker", "COBOL"])
    assert tokens == ["GIT"]
    assert unknown == ["COBOL", "Docker"]


def test_equivalent_spellings_produce_one_token():
    tokens, _ = normalize(["JS", "Javascript", "JavaScript", "React", "React.js"])
    assert tokens == ["JAVASCRIPT", "REACT"]


def test_canonical_order_of_the_assignment():
    # "Git, NodeJS, JS, Postgres, React.js" -> JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT
    tokens, _ = normalize(["Git", "NodeJS", "JS", "Postgres", "React.js"])
    assert sort_for_profile(tokens, "FULL_STACK_DEVELOPER") == [
        "JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT",
    ]


def test_order_does_not_depend_on_the_resume():
    skills = ["JS", "React.js", "NodeJS", "Postgres", "Git"]
    sequences = {
        tuple(normalize_qualifications(list(order), "FULL_STACK_DEVELOPER"))
        for order in itertools.permutations(skills)
    }
    assert len(sequences) == 1


def test_each_profile_keeps_only_its_alphabet():
    tokens, _ = normalize(["Python", "Pandas", "React", "Git"])
    assert sort_for_profile(tokens, "MACHINE_LEARNING_ENGINEER") == ["PYTHON", "PANDAS", "GIT"]
    assert sort_for_profile(tokens, "FRONTEND_DEVELOPER") == ["REACT", "GIT"]


def test_unknown_profile_is_an_error():
    with pytest.raises(ValueError):
        sort_for_profile(["GIT"], "DEVOPS_ENGINEER")


def test_seven_tuple_of_the_transducer():
    assert {str(s) for s in NORMALIZATION_FST.states} == {"q0", "q1"}
    assert {str(s) for s in NORMALIZATION_FST.start_states} == {"q0"}
    assert {str(s) for s in NORMALIZATION_FST.final_states} == {"q1"}
    assert len(NORMALIZATION_FST.input_symbols) == sum(len(v) for v in VARIANTS.values()) == 57
    assert {str(s) for s in NORMALIZATION_FST.output_symbols} == set(GLOBAL_ORDER)


def test_output_alphabet_is_the_skill_vocabulary_of_the_dsl():
    assert set(GLOBAL_ORDER) == CANONICAL_SKILLS


def test_every_profile_uses_only_canonical_tokens():
    from normalizer import CANONICAL_ORDERS

    for profile in PROFILES:
        assert set(CANONICAL_ORDERS[profile]) <= set(GLOBAL_ORDER)
