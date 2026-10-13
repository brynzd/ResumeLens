"""End-to-end tests: résumé text -> stages 1 to 4 -> validated document and Markdown."""

import pytest

import pipeline
from parser import PROJECT_ROOT
from pipeline import run_pipeline
from validator import get_validating_metamodel

RESUMES = PROJECT_ROOT / "data" / "resumes"
EXAMPLES = PROJECT_ROOT / "examples"


@pytest.fixture(scope="module")
def metamodel():
    return get_validating_metamodel()


def run(name, metamodel):
    return run_pipeline((RESUMES / name).read_text(encoding="utf-8"), metamodel)


def without_comments(text):
    return "".join(line for line in text.splitlines(keepends=True) if not line.startswith("//"))


@pytest.mark.parametrize("resume, example", [
    ("wednesday.txt", "resume_01.resume"),
    ("mary_jane.txt", "resume_02.resume"),
    ("peter_parker.txt", "resume_03.resume"),
])
def test_pipeline_writes_the_example_documents(metamodel, resume, example):
    # The examples of examples/ are the documents the pipeline generates.
    expected = without_comments((EXAMPLES / example).read_text(encoding="utf-8"))
    assert run(resume, metamodel)["document"] == expected


@pytest.mark.parametrize("resume, accepted, valid", [
    ("wednesday.txt", ["FULL_STACK_DEVELOPER"], True),
    ("mary_jane.txt", ["MACHINE_LEARNING_ENGINEER"], True),
    ("peter_parker.txt", ["FULL_STACK_DEVELOPER", "FRONTEND_DEVELOPER"], True),
    ("lisa_simpson.txt", ["DATA_ENGINEER"], True),
    ("bart_simpson.txt", [], True),
    # The fragments of the assignment satisfy their profile, but they lack the
    # mandatory parts of a candidate document, so textX rejects it.
    ("wednesday_fragment.txt", ["FULL_STACK_DEVELOPER"], False),
    ("mary_jane_fragment.txt", ["MACHINE_LEARNING_ENGINEER"], False),
])
def test_every_sample_resume(metamodel, resume, accepted, valid):
    result = run(resume, metamodel)
    assert [p for p, ok in result["verdicts"].items() if ok] == accepted
    assert (result["error"] is None) == valid, result["error"]
    assert (result["markdown"] is not None) == valid


def test_unqualified_candidate(metamodel):
    result = run("bart_simpson.txt", metamodel)
    assert result["unknown"] == ["COBOL"]
    assert "UNQUALIFIED -> ACCEPTED;" in result["document"]
    assert "- UNQUALIFIED: ACCEPTED" in result["markdown"]


def test_incomplete_fragment_reports_what_is_missing(metamodel):
    result = run("wednesday_fragment.txt", metamodel)
    assert result["missing"] == [
        "headline", "location", "contact (email, phone or linkedin)", "experience", "education",
    ]
    assert result["error"].startswith("TextXSyntaxError")


def test_cli_writes_the_results_of_every_stage(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(pipeline, "OUTPUT_DIR", tmp_path)
    pipeline.main([str(RESUMES / "wednesday.txt"), str(RESUMES / "wednesday_fragment.txt")])
    written = sorted(path.name for path in tmp_path.iterdir())
    assert written == [
        "wednesday.json", "wednesday.md", "wednesday.resume",
        "wednesday_fragment.json", "wednesday_fragment.resume",
    ]
    out = capsys.readouterr().out
    assert "FULL_STACK_DEVELOPER       ACCEPTED" in out
    assert "REJECTED: TextXSyntaxError" in out
