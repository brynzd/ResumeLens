
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

# Diccionario de mapeo de variantes (Transductor FST conceptual)
NORMALIZATION_MAP = {
    # JavaScript y variantes
    "js": "JAVASCRIPT",
    "javascript": "JAVASCRIPT",
    "ts": "TYPESCRIPT",
    "typescript": "TYPESCRIPT",

    # Frameworks frontend
    "react": "REACT",
    "react.js": "REACT",
    "reactjs": "REACT",
    "angular": "ANGULAR",
    "vue": "VUE",
    "css": "CSS",
    "tailwind": "TAILWIND",

    # Backend y Bases de datos
    "node": "NODE_JS",
    "nodejs": "NODE_JS",
    "node.js": "NODE_JS",
    "django": "DJANGO",
    "spring boot": "SPRING_BOOT",
    "postgres": "POSTGRESQL",
    "postgresql": "POSTGRESQL",
    "sql": "SQL",
    "mongodb": "MONGODB",

    # IA / Datos / DevOps
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

def normalize_qualifications(raw_technologies: list, profile_type: str) -> list:
    """
    Normaliza las variantes de tecnologías a su forma canónica y
    las ordena según la jerarquía del perfil profesional seleccionado.
    """
    # 1. Normalización de cada token encontrado
    normalized_tokens = []
    for tech in raw_technologies:
        clean_tech = tech.lower().strip()
        canonical_form = NORMALIZATION_MAP.get(clean_tech, tech.upper())
        if canonical_form not in normalized_tokens:
            normalized_tokens.append(canonical_form)

    # 2. Obtener el orden canónico del perfil correspondiente
    profile_order = CANONICAL_ORDERS.get(profile_type.upper(), [])

    # 3. Filtrar y ordenar las cualificaciones según la jerarquía del perfil
    sorted_qualifications = sorted(
        [t for t in normalized_tokens if t in profile_order],
        key=lambda x: profile_order.index(x)
    )

    return sorted_qualifications