"""The four stages end to end, on the sample résumés of data/resumes/."""

import pytest

from parser import PROJECT_ROOT
from pipeline import run_pipeline
from validator import get_validating_metamodel

METAMODEL = get_validating_metamodel()
RESUMES = PROJECT_ROOT / "data" / "resumes"


@pytest.mark.parametrize("resume, accepted, valid", [
    # The two reference résumés of the assignment
    ("wednesday.txt", ["FULL_STACK_DEVELOPER"], True),
    ("mary_jane.txt", ["MACHINE_LEARNING_ENGINEER"], True),
    # Two accepted profiles, the Data Engineer profile and an unqualified candidate
    ("peter_parker.txt", ["FULL_STACK_DEVELOPER", "FRONTEND_DEVELOPER"], True),
    ("lisa_simpson.txt", ["DATA_ENGINEER"], True),
    ("bart_simpson.txt", [], True),
    # The fragments of the assignment satisfy their profile, but they lack the
    # contact, experience and education a candidate document needs
    ("wednesday_fragment.txt", ["FULL_STACK_DEVELOPER"], False),
    ("mary_jane_fragment.txt", ["MACHINE_LEARNING_ENGINEER"], False),
])
def test_sample_resumes(resume, accepted, valid):
    result = run_pipeline((RESUMES / resume).read_text(encoding="utf-8"), METAMODEL)
    assert [profile for profile, ok in result["verdicts"].items() if ok] == accepted
    assert (result["error"] is None) == valid, result["error"]
