from pyformlang.finite_automaton import DeterministicFiniteAutomaton, State, Symbol

# Each profile pattern (src/profiles.py) is an ordered list of qualification
# categories. A resume satisfies the profile when its normalized, canonically
# sorted qualification sequence contains at least one symbol of every
# category, in category order. Extra qualifications of the same category are
# absorbed by self-loops, so an over-qualified candidate is still accepted.
#
# Stage 2 sorts with the same categories (normalizer.CANONICAL_ORDERS), which
# guarantees the input sequence always arrives category by category.
from normalizer import sort_for_profile
from profiles import PROFILE_PATTERNS, PROFILES


def create_profile_dfa(profile_type: str) -> DeterministicFiniteAutomaton:
    """
    Creates and returns a Deterministic Finite Automaton (DFA)
    for the specified professional profile using pyformlang.

    The DFA has one state per completed category: state q_i means
    "categories 1..i are already covered". From q_i, any symbol of
    category i+1 advances to q_(i+1); any additional symbol of the
    category just covered loops on q_i. Every other symbol has no
    transition, which makes the (partial) DFA reject the sequence.
    """
    pattern = PROFILE_PATTERNS.get(profile_type.upper())
    if pattern is None:
        raise ValueError(f"Unknown profile type: {profile_type}")

    dfa = DeterministicFiniteAutomaton()
    states = [State(f"q{i}") for i in range(len(pattern) + 1)]

    for i, (_category, symbols) in enumerate(pattern):
        for symbol in symbols:
            # First symbol of the category advances to the next state
            dfa.add_transition(states[i], Symbol(symbol), states[i + 1])
            # Additional symbols of the same category are absorbed
            dfa.add_transition(states[i + 1], Symbol(symbol), states[i + 1])

    dfa.add_start_state(states[0])
    dfa.add_final_state(states[-1])
    return dfa


def evaluate_resume_profile(normalized_qualifications: list, profile_type: str) -> bool:
    """
    Evaluates whether a sequence of normalized qualifications satisfies
    the acceptance pattern of the given professional profile.
    """
    dfa = create_profile_dfa(profile_type)
    # Convert list of string tokens into pyformlang symbols
    symbol_sequence = [Symbol(token) for token in normalized_qualifications]

    # Returns True if the sequence is accepted by the DFA, False otherwise
    return dfa.accepts(symbol_sequence)


def classify(normalized_tokens: list) -> dict:
    """
    Evaluates the normalized qualifications against every profile (FR-16).
    Each DFA reads the tokens of its own alphabet in its canonical order, so
    zero, one or several profiles may accept the same resume.
    """
    return {
        profile: evaluate_resume_profile(sort_for_profile(normalized_tokens, profile), profile)
        for profile in PROFILES
    }


def trace(sequence: list, profile_type: str) -> list:
    """
    Returns the states the profile DFA visits while reading the sequence.
    The run stops at the first symbol without a transition (the implicit
    trap state of the partial DFA).
    """
    dfa = create_profile_dfa(profile_type)
    delta = dfa.to_dict()
    state = dfa.start_state
    path = [str(state)]
    for token in sequence:
        state = delta.get(state, {}).get(Symbol(token))
        if state is None:
            break
        path.append(str(state))
    return path
