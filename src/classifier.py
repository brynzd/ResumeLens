from pyformlang.finite_automaton import DeterministicFiniteAutomaton, State, Symbol

def create_profile_dfa(profile_type: str) -> DeterministicFiniteAutomaton:
    """
    Creates and returns a Deterministic Finite Automaton (DFA)
    for the specified professional profile using pyformlang.
    """
    dfa = DeterministicFiniteAutomaton()

    # States definition
    q0 = State("q0")
    q1 = State("q1")
    q2 = State("q2")
    q3 = State("q3")
    q4 = State("q4")
    q5 = State("q5")

    # Configure transitions and profiles based on the project requirements
    if profile_type.upper() == "FULL_STACK":
        # Transitions for Full Stack: JAVASCRIPT -> REACT -> NODE_JS -> POSTGRESQL -> GIT
        dfa.add_transition(q0, Symbol("JAVASCRIPT"), q1)
        dfa.add_transition(q1, Symbol("REACT"), q2)
        dfa.add_transition(q2, Symbol("NODE_JS"), q3)
        dfa.add_transition(q3, Symbol("POSTGRESQL"), q4)
        dfa.add_transition(q4, Symbol("GIT"), q5)
        dfa.add_start_state(q0)
        dfa.add_final_state(q5)

    elif profile_type.upper() == "MACHINE_LEARNING":
        # Transitions for ML Engineer: PYTHON -> PANDAS -> SCIKIT_LEARN -> POSTGRESQL -> GIT
        dfa.add_transition(q0, Symbol("PYTHON"), q1)
        dfa.add_transition(q1, Symbol("PANDAS"), q2)
        dfa.add_transition(q2, Symbol("SCIKIT_LEARN"), q3)
        dfa.add_transition(q3, Symbol("POSTGRESQL"), q4)
        dfa.add_transition(q4, Symbol("GIT"), q5)
        dfa.add_start_state(q0)
        dfa.add_final_state(q5)

    elif profile_type.upper() == "FRONTEND":
        # Transitions for Frontend Developer: JAVASCRIPT -> REACT -> CSS -> GIT
        dfa.add_transition(q0, Symbol("JAVASCRIPT"), q1)
        dfa.add_transition(q1, Symbol("REACT"), q2)
        dfa.add_transition(q2, Symbol("CSS"), q3)
        dfa.add_transition(q3, Symbol("GIT"), q4)
        dfa.add_start_state(q0)
        dfa.add_final_state(q4)

    elif profile_type.upper() == "DATA_ENGINEER":
        # Transitions for Data Engineer: PYTHON -> SPARK -> POSTGRESQL -> GIT
        dfa.add_transition(q0, Symbol("PYTHON"), q1)
        dfa.add_transition(q1, Symbol("SPARK"), q2)
        dfa.add_transition(q2, Symbol("POSTGRESQL"), q3)
        dfa.add_transition(q3, Symbol("GIT"), q4)
        dfa.add_start_state(q0)
        dfa.add_final_state(q4)

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