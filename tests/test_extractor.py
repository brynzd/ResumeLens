"""Stage 1 tests: information extraction with regular expressions."""

import re

import pytest

from extractor import extract_resume_entities

# Résumé fragments of the assignment (Integrative Task 1, reference profiles).
WEDNESDAY = """Wednesday Addams
3 years of experience developing web applications.
Technical Skills:
JS, React.js, NodeJS, Postgres, Git."""

MARY_JANE = """Mary Jane Watson
 2 years of experience developing predictive models and data-processing pipelines.
Technical Skills:
 Python, Pandas, NumPy, Scikit-learn, TensorFlow, SQL, Git."""

FULL_RESUME = """Lisa Simpson
Headline: Data Engineer
Location: Springfield, Oregon
Email: lisa.simpson@springfield.edu
Phone: +1 541 555 0199
LinkedIn: https://linkedin.com/in/lisa-simpson-springfield

5 years of experience building batch and streaming data pipelines.

Technical Skills:
Python, Apache Spark, Airflow, PostgreSQL, Git

Languages:
English: native
Spanish (full professional)

Experience:
Data Engineer at Springfield Nuclear Plant (2023-02-01 - present)
- Built Airflow pipelines that load sensor data into PostgreSQL.
- Migrated nightly batch jobs from cron scripts to Spark.
Data Analyst at Kwik-E-Mart (2020-06 - 2023-01)

Education:
M.Sc. in Data Science at Springfield University (2018-08 - 2020-05)
B.Sc. in Computer Science at Springfield University (2014-08 - 2018-05)
"""

# PHONE terminal of grammar/resume.tx: an extracted phone must be writable in the DSL.
DSL_PHONE = r"\+?[0-9][0-9 ()-]{6,}[0-9]"


def test_reference_fragment_produces_the_strings_of_the_assignment():
    # Stage 1 example of the assignment: the strings are kept exactly as written.
    data = extract_resume_entities(WEDNESDAY)
    assert data["technologies"] == ["JS", "React.js", "NodeJS", "Postgres", "Git"]
    assert data["personal"]["name"] == "Wednesday Addams"
    assert data["experience_years"] == 3


def test_second_reference_fragment_keeps_tensorflow():
    data = extract_resume_entities(MARY_JANE)
    assert data["technologies"] == [
        "Python", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "SQL", "Git",
    ]
    assert data["personal"]["name"] == "Mary Jane Watson"
    assert data["experience_years"] == 2


@pytest.mark.parametrize("written", [
    "JS", "Javascript", "React.js", "ReactJS", "NodeJS", "Node.js", "Postgres", "PostgreSQL",
    "pandas", "sklearn", "scikit learn", "Scikit-learn", "Tensor Flow", "TensorFlow",
    "Py Torch", "PyTorch", "Node", "Vue.js", "Spring Boot", "Apache Spark", "Tailwind CSS",
])
def test_every_spelling_is_extracted_as_one_string(written):
    assert extract_resume_entities(f"Technical Skills: {written}.")["technologies"] == [written]


def test_skills_are_grouped_by_category():
    assert extract_resume_entities(WEDNESDAY)["skills"] == {
        "programming_languages": ["JS"],
        "frameworks_libraries": ["React.js", "NodeJS"],
        "databases": ["Postgres"],
        "tools": ["Git"],
    }


@pytest.mark.parametrize("text, expected", [
    ("Node.js and React.js", ["Node.js", "React.js"]),  # no "js" read inside them
    ("Built with Next.js", []),                          # file extension, not a language
    ("PostgreSQL, MySQL, NoSQL", ["PostgreSQL"]),        # SQL only as a whole word
    ("GitHub Actions", []),
])
def test_skills_are_whole_words(text, expected):
    assert extract_resume_entities(text)["technologies"] == expected


def test_repeated_skills_are_listed_once_in_order_of_appearance():
    text = "Technical Skills:\nReact, Git\n- Built a React front end."
    assert extract_resume_entities(text)["technologies"] == ["React", "Git"]


@pytest.mark.parametrize("phone", [
    "+57 3101234567", "+57 310 123 4567", "+1 212 555 0134", "+1 (212) 555-0134",
    "+44 20 7946 0958", "3101234567", "310-123-4567",
])
def test_phone_is_extracted_whole_and_fits_the_dsl(phone):
    found = extract_resume_entities(f"Ana Gomez\nPhone: {phone}\n")["contact"]["phone"]
    assert found == phone
    assert re.fullmatch(DSL_PHONE, found)


@pytest.mark.parametrize("text", ["Data Analyst (2018-08 - 2022-05)", "from 2019 to 2023", "Room 101"])
def test_dates_and_short_numbers_are_not_phones(text):
    assert extract_resume_entities(text)["contact"]["phone"] is None


def test_contact_information():
    contact = extract_resume_entities(FULL_RESUME)["contact"]
    assert contact == {
        "email": "lisa.simpson@springfield.edu",
        "phone": "+1 541 555 0199",
        "linkedin": "https://linkedin.com/in/lisa-simpson-springfield",
    }


@pytest.mark.parametrize("text, name", [
    ("Wednesday Addams\nFull Stack Developer\n", "Wednesday Addams"),  # does not spill into line 2
    ("Juan Pérez\n3 years of experience.\nTechnical Skills:\nJS", "Juan Pérez"),
    ("Juan de la Cruz\nPhone: +57 3101234567", "Juan de la Cruz"),
    ("WEDNESDAY ADDAMS\n3 years of experience.", "WEDNESDAY ADDAMS"),
    ("\n\n  Mary Jane Watson  \nTechnical Skills:", "Mary Jane Watson"),
    ("Technical Skills:\nJS, React", None),                              # no name line
])
def test_name_is_the_first_line(text, name):
    assert extract_resume_entities(text)["personal"]["name"] == name


@pytest.mark.parametrize("text, years", [
    ("3 years of experience developing web applications.", 3),
    ("10+ years of experience", 10),
    ("3 años de experiencia en desarrollo web", 3),
    ("Graduated 4 years ago", None),
])
def test_years_of_experience(text, years):
    assert extract_resume_entities(text)["experience_years"] == years


def test_personal_fields():
    personal = extract_resume_entities(FULL_RESUME)["personal"]
    assert personal == {
        "name": "Lisa Simpson",
        "headline": "Data Engineer",
        "location": "Springfield, Oregon",
        "summary": None,
    }


def test_experience_entries_with_tasks():
    assert extract_resume_entities(FULL_RESUME)["experience"] == [
        {
            "title": "Data Engineer",
            "organization": "Springfield Nuclear Plant",
            "start": "2023-02-01",
            "end": "present",
            "tasks": [
                "Built Airflow pipelines that load sensor data into PostgreSQL.",
                "Migrated nightly batch jobs from cron scripts to Spark.",
            ],
        },
        {
            "title": "Data Analyst",
            "organization": "Kwik-E-Mart",
            "start": "2020-06",
            "end": "2023-01",
            "tasks": [],
        },
    ]


def test_education_entries_and_academic_qualifications():
    data = extract_resume_entities(FULL_RESUME)
    assert [(d["title"], d["organization"]) for d in data["education"]] == [
        ("M.Sc. in Data Science", "Springfield University"),
        ("B.Sc. in Computer Science", "Springfield University"),
    ]
    assert data["academic_qualifications"] == ["M.Sc.", "B.Sc.", "Computer Science"]


def test_languages():
    assert extract_resume_entities(FULL_RESUME)["languages"] == [
        {"name": "English", "level": "native"},
        {"name": "Spanish", "level": "full_professional"},
    ]


def test_other_qualifications():
    found = extract_resume_entities(MARY_JANE)["other_qualifications"]
    assert found == ["predictive models", "data-processing pipelines"]
    assert extract_resume_entities("Built REST APIs.")["other_qualifications"] == ["REST APIs"]


def test_missing_information_is_none_or_empty():
    data = extract_resume_entities(WEDNESDAY)
    assert data["contact"] == {"email": None, "phone": None, "linkedin": None}
    assert data["experience"] == [] and data["education"] == [] and data["languages"] == []
