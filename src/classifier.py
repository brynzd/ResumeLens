"""Stage 3: recognize the pattern of every profile with a DFA.

docs/automata.md gives the 5-tuple and the diagram of each automaton.
"""

from pyformlang.finite_automaton import DeterministicFiniteAutomaton, State, Symbol

from normalizer import sort_for_profile
from profiles import PROFILE_PATTERNS, PROFILES


def create_profile_dfa(profile):
    """DFA of a profile, where state q_i means "the first i categories are covered".

    A token of the next category advances to the next state, and another token
    of the category just covered loops on the same state. Any other token has
    no transition, so the sequence is rejected.
    """
    pattern = PROFILE_PATTERNS[profile]
    states = [State(f"q{i}") for i in range(len(pattern) + 1)]

    dfa = DeterministicFiniteAutomaton()
    dfa.add_start_state(states[0])
    dfa.add_final_state(states[-1])
    for i, (_category, tokens) in enumerate(pattern):
        for token in tokens:
            dfa.add_transition(states[i], Symbol(token), states[i + 1])
            dfa.add_transition(states[i + 1], Symbol(token), states[i + 1])
    return dfa


PROFILE_DFAS = {profile: create_profile_dfa(profile) for profile in PROFILES}


def evaluate_resume_profile(sequence, profile):
    """True if the DFA of the profile accepts the sorted sequence of tokens."""
    return PROFILE_DFAS[profile].accepts([Symbol(token) for token in sequence])


def classify(tokens):
    """Verdict of every profile for the canonical tokens of a résumé."""
    verdicts = {}
    for profile in PROFILES:
        sequence = sort_for_profile(tokens, profile)
        verdicts[profile] = evaluate_resume_profile(sequence, profile)
    return verdicts


def trace(sequence, profile):
    """States the DFA visits while reading the sequence, until a missing transition."""
    dfa = PROFILE_DFAS[profile]
    transitions = dfa.to_dict()
    state = dfa.start_state
    path = [str(state)]
    for token in sequence:
        state = transitions[state].get(Symbol(token))
        if state is None:
            break
        path.append(str(state))
    return path
