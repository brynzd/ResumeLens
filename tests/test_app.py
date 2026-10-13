"""UI tests: the Streamlit app runs the four stages (streamlit.testing, no browser)."""

import pytest

pytest.importorskip("streamlit")

from streamlit.testing.v1 import AppTest  # noqa: E402

from parser import PROJECT_ROOT  # noqa: E402

APP = str(PROJECT_ROOT / "src" / "app.py")
FRAGMENT = (PROJECT_ROOT / "data" / "resumes" / "wednesday_fragment.txt").read_text(encoding="utf-8")


def start():
    app = AppTest.from_file(APP, default_timeout=60)
    app.run()
    return app


def run_pipeline(app, text=None, sample=None):
    if text is not None:
        app.sidebar.radio[0].set_value("Paste Resume Text").run()
        app.sidebar.text_area[0].set_value(text)
    if sample is not None:
        app.sidebar.selectbox[0].set_value(sample)
    app.sidebar.button[0].click().run()
    assert not app.exception
    return app


def test_first_load_asks_for_a_resume():
    app = start()
    assert not app.exception
    assert "Run Pipeline" in app.info[0].value


def test_sample_resume_goes_through_the_four_stages():
    app = run_pipeline(start(), sample="wednesday.txt")
    assert [tab.label for tab in app.tabs] == [
        "📋 1 · Extraction (regex)",
        "🔄 2 · Normalization (FST)",
        "🤖 3 · Recognition (DFA)",
        "🧾 4 · Candidate document (textX)",
    ]
    assert "Full Stack Developer" in app.success[0].value
    assert "**FULL_STACK_DEVELOPER**: ACCEPTED" in [s.value for s in app.success]
    assert "**DATA_ENGINEER**: REJECTED" in [e.value for e in app.error]
    assert app.code[0].value.startswith('candidate "Wednesday Addams" {')
    assert any("textX accepted the document" in s.value for s in app.success)


def test_several_accepted_profiles_are_reported():
    app = run_pipeline(start(), sample="peter_parker.txt")
    assert app.success[0].value == "Accepted profiles: Full Stack Developer, Frontend Developer"


def test_pasted_fragment_is_classified_but_its_document_is_incomplete():
    app = run_pipeline(start(), text=FRAGMENT)
    assert "**FULL_STACK_DEVELOPER**: ACCEPTED" in [s.value for s in app.success]
    assert "headline" in app.warning[0].value
    assert any(e.value.startswith("textX rejected the document") for e in app.error)


def test_unqualified_candidate():
    app = run_pipeline(start(), sample="bart_simpson.txt")
    assert "UNQUALIFIED" in app.error[0].value
