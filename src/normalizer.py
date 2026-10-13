"""Stage 2: normalize the extracted skills with a finite-state transducer.

docs/transducers.md gives the formal definition M = (Q, Σ, Γ, δ, ω, q0, F).
"""

from pyformlang.finite_automaton import State, Symbol
from pyformlang.fst import FST

from profiles import PROFILE_PATTERNS

# Canonical token -> the spellings it normalizes, in lowercase and with one
# space between words. The spellings are the input alphabet Σ and the tokens
# the output alphabet Γ, in the global order used to list the skills.
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

GLOBAL_ORDER = list(VARIANTS)


def create_normalization_fst():
    """Transducer with one transition q0 -> q1 per spelling, which writes its token."""
    fst = FST()
    q0 = State("q0")
    q1 = State("q1")
    fst.add_start_state(q0)
    fst.add_final_state(q1)
    for token, spellings in VARIANTS.items():
        for spelling in spellings:
            fst.add_transition(q0, Symbol(spelling), q1, [Symbol(token)])
    return fst


NORMALIZATION_FST = create_normalization_fst()


def clean(raw):
    """Write an extracted string as an input symbol: lowercase, single spaces."""
    return " ".join(raw.lower().split())


def translate(raw):
    """Canonical token of an extracted string, or None if the transducer rejects it."""
    outputs = list(NORMALIZATION_FST.translate([clean(raw)]))
    if not outputs:
        return None
    return str(outputs[0][0])


def normalize(raw_technologies):
    """Translate the extracted strings.

    Returns the canonical tokens without duplicates and the strings the
    transducer does not know, both in order of appearance.
    """
    tokens = []
    unknown = []
    for raw in raw_technologies:
        token = translate(raw)
        if token is None:
            if raw not in unknown:
                unknown.append(raw)
        elif token not in tokens:
            tokens.append(token)
    return tokens, unknown


def canonical_order(profile):
    """Tokens of a profile, category by category."""
    order = []
    for _category, tokens in PROFILE_PATTERNS[profile]:
        order += tokens
    return order


def sort_for_profile(tokens, profile):
    """The tokens that belong to the profile, in its canonical order."""
    return [token for token in canonical_order(profile) if token in tokens]
