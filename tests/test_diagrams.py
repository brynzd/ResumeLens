"""The committed diagrams match the code (regenerate them with python src/diagrams.py)."""

import pytest

from diagrams import DFA_FILES, DIAGRAMS, dfa_dot, fst_dot
from parser import PROJECT_ROOT


@pytest.mark.parametrize("profile", DFA_FILES)
def test_dfa_diagram_matches_the_profile_pattern(profile):
    assert (DIAGRAMS / f"{DFA_FILES[profile]}.dot").read_text(encoding="utf-8") == dfa_dot(profile)


def test_transducer_diagram_matches_the_variants():
    assert (DIAGRAMS / "fst_normalization.dot").read_text(encoding="utf-8") == fst_dot()


@pytest.mark.parametrize(
    "example", sorted((PROJECT_ROOT / "examples").glob("*.resume")), ids=lambda path: path.name
)
def test_every_example_has_its_parse_tree(example):
    for name in (f"{example.stem}_tree.dot", f"{example.stem}_tree.dot.png"):
        assert (DIAGRAMS / name).is_file(), name
