"""Stage 2 - normalize the extracted skill strings with a finite-state transducer.

The transducer M = (Q, Σ, Γ, δ, ω, q0, F) reads one extracted string as a
single input symbol and writes its canonical token (docs/transducers.md):

- Q = {q0, q1}, initial state q0, F = {q1};
- Σ = every spelling listed in VARIANTS;
- Γ = the canonical tokens, the keys of VARIANTS;
- δ(q0, v) = q1 and ω(q0, v) = the canonical token of v, for every v in Σ.

A string outside Σ has no transition, so the transducer rejects it and it
is reported as unknown instead of being guessed (FR-12). The canonical
tokens are then deduplicated (FR-13) and, for every profile, sorted in its
canonical order (FR-14) before stage 3.
"""

from pyformlang.fst import FST
from pyformlang.finite_automaton import State, Symbol

from profiles import PROFILE_PATTERNS

# Canonical token -> spellings it normalizes, written the way stage 2 cleans
# them (lowercase, one space between words). The keys are the output
# alphabet in the global canonical order of docs/domain.md, and together
# the spellings cover every string the stage-1 skill patterns extract
# (except the tools no profile uses: Docker, Kubernetes, AWS, GCP, Terraform).
VARIANTS = {
    "JAVASCRIPT": ["js", "javascript", "java script"],
    "TYPESCRIPT": ["ts", "typescript", "type script"],
    "PYTHON": ["python", "python3"],
    "SCALA": ["scala"],
    "REACT": ["react", "reactjs", "react.js", "react js"],
    "ANGULAR": ["angular", "angularjs", "angular.js", "angular js"],
    "VUE": ["vue", "vuejs", "vue.js", "vue js"],
    "CSS": ["css", "css3"],
    "TAILWIND": ["tailwind", "tailwindcss", "tailwind css"],
    "NODE_JS": ["node", "nodejs", "node.js", "node js"],
    "DJANGO": ["django"],
    "SPRING_BOOT": ["spring boot", "springboot", "spring-boot"],
    "PANDAS": ["pandas"],
    "NUMPY": ["numpy", "num py"],
    "SCIKIT_LEARN": ["sklearn", "scikit-learn", "scikit learn", "scikitlearn"],
    "TENSORFLOW": ["tensorflow", "tensor flow"],
    "PYTORCH": ["pytorch", "py torch"],
    "SPARK": ["spark", "apache spark", "pyspark"],
    "AIRFLOW": ["airflow", "apache airflow"],
    "POSTGRESQL": ["postgres", "postgresql"],
    "MONGODB": ["mongodb", "mongo", "mongo db"],
    "SQL": ["sql"],
    "GIT": ["git"],
}

# Global canonical order, used to list the skills of a candidate document.
GLOBAL_ORDER = list(VARIANTS)

# Canonical order of every profile: the tokens of its categories, category
# by category (src/profiles.py). Sorting with it makes the sequence the
# stage-3 automaton reads independent of the order of the résumé.
CANONICAL_ORDERS = {
    profile: [token for _category, tokens in pattern for token in tokens]
    for profile, pattern in PROFILE_PATTERNS.items()
}


def clean(raw: str) -> str:
    """Write an extracted string as an input symbol: lowercase, single spaces."""
    return " ".join(raw.lower().split())


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

    # One transition per spelling: read the spelling, write its canonical token
    for canonical, spellings in VARIANTS.items():
        for spelling in spellings:
            fst.add_transition(q0, Symbol(spelling), q1, [Symbol(canonical)])

    return fst


NORMALIZATION_FST = create_normalization_fst()


def translate(raw: str):
    """Canonical token of one extracted string, or None if the FST rejects it."""
    for output in NORMALIZATION_FST.translate([clean(raw)]):
        return "".join(str(symbol) for symbol in output)
    return None


def normalize(raw_technologies: list) -> tuple:
    """
    Translate every extracted string. Returns the canonical tokens without
    duplicates, in order of first appearance, and the strings the
    transducer does not know, as written.
    """
    tokens, unknown = [], []
    for raw in raw_technologies:
        token = translate(raw)
        if token is None:
            if raw not in unknown:
                unknown.append(raw)
        elif token not in tokens:
            tokens.append(token)
    return tokens, unknown


def sort_for_profile(tokens: list, profile_type: str) -> list:
    """The tokens of the profile's alphabet, in the profile's canonical order."""
    order = CANONICAL_ORDERS.get(profile_type.upper())
    if order is None:
        raise ValueError(f"Unknown profile type: {profile_type}")
    return sorted((token for token in tokens if token in order), key=order.index)


def normalize_qualifications(raw_technologies: list, profile_type: str) -> list:
    """
    Normalizes technology variants using the pyformlang FST and
    sorts them according to the hierarchical order of the selected profile.
    """
    tokens, _unknown = normalize(raw_technologies)
    return sort_for_profile(tokens, profile_type)
