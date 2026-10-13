"""Stage 4: the candidate profile DSL (textX grammar, validation and Markdown)."""

import pytest

from markdown_generator import OUTPUT_DIR, generate_markdown
from parser import PROJECT_ROOT
from validator import collect_cases, get_validating_metamodel, validate_file

METAMODEL = get_validating_metamodel()
CASES = collect_cases()
EXAMPLES = sorted((PROJECT_ROOT / "examples").glob("*.resume"))


@pytest.mark.parametrize("path, valid", CASES, ids=[path.name for path, _ in CASES])
def test_valid_documents_are_accepted_and_invalid_ones_rejected(path, valid):
    error = validate_file(path, METAMODEL)
    if valid:
        assert error is None, error
    else:
        assert error is not None, "accepted, but it must be rejected"


@pytest.mark.parametrize("path", EXAMPLES, ids=[path.name for path in EXAMPLES])
def test_markdown_of_the_examples(path):
    model = METAMODEL.model_from_file(path)
    expected = (OUTPUT_DIR / f"{path.stem}.md").read_text(encoding="utf-8")
    assert generate_markdown(model) == expected
