"""The four professional profiles, defined once for stages 2 and 3."""

# Each profile is an ordered list of categories, and each category lists the
# canonical tokens that satisfy it. The names are the ones of the DSL.
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

PROFILE_NAMES = {
    "FULL_STACK_DEVELOPER": "Full Stack Developer",
    "MACHINE_LEARNING_ENGINEER": "Machine Learning Engineer",
    "FRONTEND_DEVELOPER": "Frontend Developer",
    "DATA_ENGINEER": "Data Engineer",
}

PROFILES = list(PROFILE_PATTERNS)
