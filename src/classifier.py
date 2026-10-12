from pyformlang.finite_automaton import DeterministicFiniteAutomaton, State, Symbol

def create_profile_dfa(profile_type: str) -> DeterministicFiniteAutomaton:
    """
    Creates a flexible Deterministic Finite Automaton (DFA) for the specified
    professional profile, allowing alternative paths and optional tool sequences.
    """
    dfa = DeterministicFiniteAutomaton()

    q0 = State("q0") # Initial state
    q1 = State("q1") # Core frontend/lang
    q2 = State("q2") # Core framework
    q3 = State("q3") # Backend/Data
    q4 = State("q4") # Database
    q5 = State("q5") # Final accepting state (Git or final required tool)

    dfa.add_start_state(q0)
    dfa.add_final_state(q5)

    profile = profile_type.upper()

    if profile == "FULL_STACK":
        # Flexible transitions allowing JavaScript or TypeScript as start, etc.
        dfa.add_transition(q0, Symbol("JAVASCRIPT"), q1)
        dfa.add_transition(q0, Symbol("TYPESCRIPT"), q1)

        dfa.add_transition(q1, Symbol("REACT"), q2)
        dfa.add_transition(q1, Symbol("ANGULAR"), q2)
        dfa.add_transition(q1, Symbol("VUE"), q2)

        dfa.add_transition(q2, Symbol("NODE_JS"), q3)
        dfa.add_transition(q2, Symbol("DJANGO"), q3)

        dfa.add_transition(q3, Symbol("POSTGRESQL"), q4)
        dfa.add_transition(q3, Symbol("MONGODB"), q4)

        # Git can loop or lead directly to final state
        dfa.add_transition(q4, Symbol("GIT"), q5)
        dfa.add_transition(q4, Symbol("POSTGRESQL"), q4) # Allow self-loops for multiple DBs if needed

    elif profile == "MACHINE_LEARNING":
        dfa.add_transition(q0, Symbol("PYTHON"), q1)
        dfa.add_transition(q1, Symbol("PANDAS"), q2)
        dfa.add_transition(q1, Symbol("NUMPY"), q2)

        dfa.add_transition(q2, Symbol("SCIKIT_LEARN"), q3)
        dfa.add_transition(q2, Symbol("TENSORFLOW"), q3)
        dfa.add_transition(q2, Symbol("PYTORCH"), q3)

        dfa.add_transition(q3, Symbol("POSTGRESQL"), q4)
        dfa.add_transition(q3, Symbol("SQL"), q4)

        dfa.add_transition(q4, Symbol("GIT"), q5)

    elif profile == "FRONTEND":
        dfa.add_transition(q0, Symbol("JAVASCRIPT"), q1)
        dfa.add_transition(q0, Symbol("TYPESCRIPT"), q1)
        dfa.add_transition(q1, Symbol("REACT"), q2)
        dfa.add_transition(q2, Symbol("CSS"), q3)
        dfa.add_transition(q3, Symbol("GIT"), q4)
        # Ajustamos estado final para frontend si termina en q4
        dfa.add_final_state(q4)

    elif profile == "DATA_ENGINEER":
        dfa.add_transition(q0, Symbol("PYTHON"), q1)
        dfa.add_transition(q0, Symbol("SCALA"), q1)
        dfa.add_transition(q1, Symbol("SPARK"), q2)
        dfa.add_transition(q2, Symbol("AIRFLOW"), q3)
        dfa.add_transition(q3, Symbol("POSTGRESQL"), q4)
        dfa.add_transition(q4, Symbol("GIT"), q5)

    return dfa

def evaluate_resume_profile(normalized_qualifications: list, profile_type: str) -> bool:
    """
    Evaluates whether a normalized sequence of skills satisfies the flexible DFA.
    """
    dfa = create_profile_dfa(profile_type)
    symbol_sequence = [Symbol(token) for token in normalized_qualifications]
    return dfa.accepts(symbol_sequence)