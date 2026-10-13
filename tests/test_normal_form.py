"""RAA3: the Chomsky Normal Form of the classification grammar (docs/normal_forms.md)."""

from itertools import product

import pytest
from pyformlang.cfg import CFG, Variable

from parser import PROJECT_ROOT, get_metamodel

# pyformlang reads capitalized words as variables, so the tokens are written as
# lowercase names: lbrace = "{", rbrace = "}", arrow = "->", semicolon = ";".
PROFILES = ["full_stack_developer", "machine_learning_engineer", "frontend_developer",
            "data_engineer", "unqualified"]
VERDICTS = ["accepted", "rejected"]
ALTERNATIVES = f"""
P -> {' | '.join(PROFILES)}
V -> {' | '.join(VERDICTS)}
"""

# Step 1: the EBNF repetition written as a context-free grammar.
BNF = """
C -> classification lbrace L rbrace
L -> R | R L
R -> P arrow V semicolon
""" + ALTERNATIVES

# Step 4: the grammar in Chomsky Normal Form.
CNF = """
C -> Tc X1
X1 -> Tl X2
X2 -> L Tr
L -> P Y1 | R L
R -> P Y1
Y1 -> Ta Y2
Y2 -> V Ts
Tc -> classification
Tl -> lbrace
Tr -> rbrace
Ta -> arrow
Ts -> semicolon
""" + ALTERNATIVES


def grammar(text):
    return CFG.from_text(text, start_symbol=Variable("C"))


def block(results):
    return ["classification", "lbrace", *[t for r in results for t in r], "rbrace"]


RESULTS = [[p, "arrow", v, "semicolon"] for p, v in product(PROFILES, VERDICTS)]
VALID = [block(rs) for k in (1, 2) for rs in product(RESULTS, repeat=k)]
INVALID = [w[:i] + w[i + 1:] for w in VALID for i in range(len(w))]


@pytest.fixture(scope="module")
def grammars():
    bnf, cnf = grammar(BNF), grammar(CNF)
    return {"bnf": bnf, "cnf": cnf, "pyformlang": bnf.to_normal_form()}


def test_only_the_converted_grammar_is_in_normal_form(grammars):
    assert not grammars["bnf"].is_normal_form()
    assert grammars["cnf"].is_normal_form()
    assert len(grammars["cnf"].productions) == 20


@pytest.mark.parametrize("name", ["bnf", "cnf", "pyformlang"])
def test_the_grammars_generate_the_same_blocks(grammars, name):
    assert len(VALID) == 110 and len(INVALID) == 1170
    assert all(grammars[name].contains(w) for w in VALID)
    assert not any(grammars[name].contains(w) for w in INVALID)


def test_cnf_accepts_the_classification_of_every_example(grammars):
    metamodel = get_metamodel()
    for path in sorted((PROJECT_ROOT / "examples").glob("*.resume")):
        items = metamodel.model_from_file(path).classification.items
        results = [[r.profile.lower(), "arrow", r.verdict.lower(), "semicolon"] for r in items]
        assert grammars["cnf"].contains(block(results)), path.name
