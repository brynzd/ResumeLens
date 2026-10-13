"""Stage 1: extraction with regular expressions."""

from pathlib import Path

from extractor import extract_resume_entities

RESUMES = Path(__file__).resolve().parent.parent / "data" / "resumes"


def extract(name):
    return extract_resume_entities((RESUMES / name).read_text(encoding="utf-8"))


def test_example_of_the_assignment():
    # Wednesday Addams fragment: the strings are kept exactly as written
    data = extract("wednesday_fragment.txt")
    assert data["technologies"] == ["JS", "React.js", "NodeJS", "Postgres", "Git"]
    assert data["personal"]["name"] == "Wednesday Addams"
    assert data["experience_years"] == 3


def test_second_reference_fragment():
    data = extract("mary_jane_fragment.txt")
    assert data["technologies"] == [
        "Python", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "SQL", "Git",
    ]
    assert data["other_qualifications"] == ["predictive models", "data-processing pipelines"]
    assert data["experience_years"] == 2


def test_skills_by_category():
    assert extract("wednesday_fragment.txt")["skills"] == {
        "programming_languages": ["JS"],
        "frameworks_libraries": ["React.js", "NodeJS"],
        "databases": ["Postgres"],
        "tools": ["Git"],
        "unrecognized": [],
    }


def test_personal_and_contact_information():
    data = extract("peter_parker.txt")
    assert data["personal"]["headline"] == "Frontend Developer"
    assert data["personal"]["location"] == "Queens, New York"
    assert data["contact"] == {
        "email": "peter.parker@dailybugle.com",
        "phone": "+1 718 555 0110",
        "linkedin": "https://linkedin.com/in/peter-parker-queens",
    }


def test_professional_experience():
    data = extract("peter_parker.txt")
    assert data["experience_years"] == 4
    assert data["experience"] == [
        {
            "title": "Frontend Developer",
            "organization": "Daily Bugle",
            "start": "2023-03-01",
            "end": "present",
            "tasks": [
                "Rebuilt the photo gallery with Vue.js and Tailwind CSS.",
                "Wrote the Node.js service that publishes photos to PostgreSQL.",
            ],
        },
        {
            "title": "Web Intern",
            "organization": "Oscorp",
            "start": "2022-06",
            "end": "2022-12",
            "tasks": [],
        },
    ]


def test_academic_qualifications_and_languages():
    data = extract("peter_parker.txt")
    assert [degree["title"] for degree in data["education"]] == [
        "B.Sc. in Physics", "Web Development Diploma",
    ]
    assert data["academic_qualifications"] == ["B.Sc.", "Diploma"]
    assert data["languages"] == [
        {"name": "English", "level": "native"},
        {"name": "Spanish", "level": "professional"},
    ]


def test_unknown_listed_skill_is_kept():
    data = extract("bart_simpson.txt")
    assert data["skills"]["unrecognized"] == ["COBOL"]
    assert data["technologies"] == ["Git", "COBOL"]


def test_missing_information_is_empty():
    data = extract("wednesday_fragment.txt")
    assert data["contact"] == {"email": None, "phone": None, "linkedin": None}
    assert data["experience"] == [] and data["education"] == []
