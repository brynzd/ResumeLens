"""The four professional profiles of ResumeLens, defined once as data.

Each profile is an ordered list of qualification categories, and each
category lists the canonical tokens (output alphabet of the stage-2
transducer) that satisfy it. The whole pipeline reads this data (FR-03):

- stage 2 sorts the normalized qualifications in the canonical order of a
  profile (``normalizer.CANONICAL_ORDERS``: its categories, in order);
- stage 3 builds one DFA per profile from the same categories
  (``classifier.create_profile_dfa``).

The profile names are the ones of the candidate profile DSL
(``Profile`` rule in ``grammar/resume.tx``).
"""

PROFILE_PATTERNS = {
    "FULL_STACK_DEVELOPER": [
        ("language", ["JAVASCRIPT", "TYPESCRIPT"]),
        ("frontend", ["REACT", "ANGULAR", "VUE"]),
        ("backend", ["NODE_JS", "DJANGO", "SPRING_BOOT"]),
        ("database", ["POSTGRESQL", "MONGODB", "SQL"]),
        ("version_control", ["GIT"]),
    ],
    "MACHINE_LEARNING_ENGINEER": [
        ("language", ["PYTHON"]),
        ("data_processing", ["PANDAS", "NUMPY"]),
        ("ml_framework", ["SCIKIT_LEARN", "TENSORFLOW", "PYTORCH"]),
        ("database", ["POSTGRESQL", "SQL"]),
        ("version_control", ["GIT"]),
    ],
    "FRONTEND_DEVELOPER": [
        ("language", ["JAVASCRIPT", "TYPESCRIPT"]),
        ("framework", ["REACT", "ANGULAR", "VUE"]),
        ("styling", ["CSS", "TAILWIND"]),
        ("version_control", ["GIT"]),
    ],
    "DATA_ENGINEER": [
        ("language", ["PYTHON", "SCALA"]),
        ("pipeline", ["SPARK", "AIRFLOW"]),
        ("database", ["POSTGRESQL", "SQL"]),
        ("version_control", ["GIT"]),
    ],
}

# Human-readable names, for the UI and the documents.
PROFILE_NAMES = {
    "FULL_STACK_DEVELOPER": "Full Stack Developer",
    "MACHINE_LEARNING_ENGINEER": "Machine Learning Engineer",
    "FRONTEND_DEVELOPER": "Frontend Developer",
    "DATA_ENGINEER": "Data Engineer",
}

PROFILES = list(PROFILE_PATTERNS)
