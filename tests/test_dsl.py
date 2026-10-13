"""Stage 4 tests: the candidate profile DSL (textX grammar, validation, Markdown)."""

import pytest

from markdown_generator import OUTPUT_DIR, generate_markdown
from parser import PROJECT_ROOT
from validator import collect_cases, get_validating_metamodel, validate_file

EXAMPLES = sorted((PROJECT_ROOT / "examples").glob("*.resume"))


@pytest.fixture(scope="module")
def metamodel():
    return get_validating_metamodel()


@pytest.mark.parametrize(
    "path, should_be_valid",
    collect_cases(),
    ids=lambda case: case.name if hasattr(case, "name") else None,
)
def test_specification_is_accepted_or_rejected(metamodel, path, should_be_valid):
    error = validate_file(path, metamodel)
    assert (error is None) == should_be_valid, error or "accepted, but it must be rejected"


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda path: path.name)
def test_committed_markdown_is_up_to_date(metamodel, path):
    model = metamodel.model_from_file(path)
    expected = (OUTPUT_DIR / f"{path.stem}.md").read_text(encoding="utf-8")
    assert generate_markdown(model) == expected


def test_there_are_at_least_three_examples():
    assert len(EXAMPLES) >= 3


def test_examples_exercise_different_parts_of_the_language(metamodel):
    models = [metamodel.model_from_file(path) for path in EXAMPLES]
    accepted = {
        tuple(r.profile for r in m.classification.items if r.verdict == "ACCEPTED") for m in models
    }
    assert len(accepted) == len(models)  # different classifications
    assert any(m.languages for m in models)
    assert any(len(m.experiences.items) > 1 for m in models)
    assert any(len(m.education.items) > 1 for m in models)
    assert any(m.contact.phone for m in models) and any(m.contact.linkedin for m in models)
