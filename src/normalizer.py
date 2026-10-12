from pyformlang.fst import FST
from pyformlang.finite_automaton import State, Symbol

# Canonical orders defined for the 4 professional profiles of the project
CANONICAL_ORDERS = {
    "FULL_STACK": [
        "JAVASCRIPT", "TYPESCRIPT",
        "REACT", "ANGULAR", "VUE",
        "NODE_JS", "DJANGO", "SPRING_BOOT",
        "POSTGRESQL", "MONGODB",
        "GIT"
    ],
    "MACHINE_LEARNING": [
        "PYTHON",
        "PANDAS", "NUMPY",
        "SCIKIT_LEARN", "TENSORFLOW", "PYTORCH",
        "POSTGRESQL", "SQL",
        "GIT"
    ],
    "FRONTEND": [
        "JAVASCRIPT", "TYPESCRIPT",
        "REACT", "ANGULAR", "VUE",
        "CSS", "TAILWIND",
        "GIT"
    ],
    "DATA_ENGINEER": [
        "PYTHON", "SCALA",
        "SPARK", "AIRFLOW",
        "POSTGRESQL", "SQL",
        "GIT"
    ]
}

def create_normalization_fst() -> FST:
    """
    Creates and returns a real Finite-State Transducer (FST) using pyformlang
    to map technology variants and abbreviations to their canonical forms.
    """
    fst = FST()

    # States definition
    q0 = State("q0")  # Initial state
    q1 = State("q1")  # Accepting state

    fst.add_start_state(q0)
    fst.add_final_state(q1)

    # Dictionary of variant mappings (Input variant -> Canonical output symbol)
    variant_mappings = {
        # JavaScript / TypeScript
        "js": "JAVASCRIPT",
        "javascript": "JAVASCRIPT",
        "ts": "TYPESCRIPT",
        "typescript": "TYPESCRIPT",

        # Frontend frameworks and styles
        "react": "REACT",
        "react.js": "REACT",
        "reactjs": "REACT",
        "angular": "ANGULAR",
        "vue": "VUE",
        "css": "CSS",
        "tailwind": "TAILWIND",

        # Backend and Databases
        "node": "NODE_JS",
        "nodejs": "NODE_JS",
        "node.js": "NODE_JS",
        "django": "DJANGO",
        "spring boot": "SPRING_BOOT",
        "postgres": "POSTGRESQL",
        "postgresql": "POSTGRESQL",
        "sql": "SQL",
        "mongodb": "MONGODB",

        # AI / Data / DevOps
        "python": "PYTHON",
        "scala": "SCALA",
        "pandas": "PANDAS",
        "numpy": "NUMPY",
        "sklearn": "SCIKIT_LEARN",
        "scikit-learn": "SCIKIT_LEARN",
        "scikit learn": "SCIKIT_LEARN",
        "tensorflow": "TENSORFLOW",
        "pytorch": "PYTORCH",
        "spark": "SPARK",
        "apache spark": "SPARK",
        "airflow": "AIRFLOW",
        "apache airflow": "AIRFLOW",
        "git": "GIT"
    }

    # Add transitions to the FST for each mapping variant
    for variant, canonical in variant_mappings.items():
        fst.add_transition(
            q0,
            Symbol(variant.lower().strip()),
            q1,
            [Symbol(canonical)]
        )

    return fst

def normalize_qualifications(raw_technologies: list, profile_type: str) -> list:
    """
    Normalizes technology variants using the pyformlang FST and
    sorts them according to the hierarchical order of the selected profile.
    """
    fst = create_normalization_fst()
    normalized_tokens = []

    for tech in raw_technologies:
        clean_tech = tech.lower().strip()
        # Translate the token using the FST
        results = list(fst.translate([clean_tech]))

        if results:
            # Extract the translated symbol from the FST result sequence
            canonical_form = "".join(str(s) for s in results[0])
            if canonical_form not in normalized_tokens:
                normalized_tokens.append(canonical_form)
        else:
            # Fallback if the variant is not explicitly in the FST
            fallback = tech.upper()
            if fallback not in normalized_tokens:
                normalized_tokens.append(fallback)

    # Retrieve the canonical order for the corresponding profile
    profile_order = CANONICAL_ORDERS.get(profile_type.upper(), [])

    # Filter and sort qualifications based on the profile's hierarchy
    sorted_qualifications = sorted(
        [t for t in normalized_tokens if t in profile_order],
        key=lambda x: profile_order.index(x)
    )

    return sorted_qualifications