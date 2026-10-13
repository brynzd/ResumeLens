# Chomsky Normal Form of the Classification Grammar

Learning outcome RAA3 asks to simplify grammars with normal forms. textX does not
need a normal form: it parses with a PEG, a recursive-descent parser with ordered
choice. The **Chomsky Normal Form (CNF)** is the form the CYK membership algorithm
requires, and converting a part of the DSL grammar shows every simplification step.
This document converts the `classification` section of the DSL
([`grammar.md`](grammar.md)) and checks the result with pyformlang
([`tests/test_normal_form.py`](../tests/test_normal_form.py)).

A context-free grammar is in CNF when every production has the form **A → BC** (two
variables) or **A → a** (one terminal); λ may only be produced by the start symbol,
and only if the start symbol does not appear on any right-hand side.

## 0. The fragment, in EBNF

```ebnf
Classification ::= "classification" "{" Result { Result } "}" ;
Result         ::= Profile "->" Verdict ";" ;
Profile        ::= "FULL_STACK_DEVELOPER" | "MACHINE_LEARNING_ENGINEER"
                 | "FRONTEND_DEVELOPER" | "DATA_ENGINEER" | "UNQUALIFIED" ;
Verdict        ::= "ACCEPTED" | "REJECTED" ;
```

The terminals are the tokens of the language: `classification`, `{`, `}`, `->`,
`;`, the five profiles and the two verdicts.

## 1. From EBNF to a context-free grammar

EBNF repetition is not a production of a CFG. `Result { Result }` (one or more
results) becomes a new variable *L* with a right-recursive rule:

G = (Σ, N, S, P) with N = {C, L, R, P, V}, S = C and the productions

```
C → classification { L }
L → R | R L
R → P -> V ;
P → FULL_STACK_DEVELOPER | MACHINE_LEARNING_ENGINEER | FRONTEND_DEVELOPER
  | DATA_ENGINEER | UNQUALIFIED
V → ACCEPTED | REJECTED
```

## 2. Simplification

1. **λ-productions.** No variable derives λ (every rule produces at least one
   terminal), so there is nothing to remove.
2. **Unit productions.** *L → R* has a single variable as body. It is replaced by
   the bodies of *R*: *L → P -> V ;*.
3. **Useless symbols.** Every variable derives a string of terminals (it is
   *generating*) and appears in a derivation from *C* (it is *reachable*), so none
   is removed.

```
C → classification { L }
L → P -> V ; | R L
R → P -> V ;
P → FULL_STACK_DEVELOPER | MACHINE_LEARNING_ENGINEER | FRONTEND_DEVELOPER
  | DATA_ENGINEER | UNQUALIFIED
V → ACCEPTED | REJECTED
```

## 3. Terminals in long bodies

In a body of two or more symbols every terminal is replaced by a new variable that
produces only that terminal: T_c → classification, T_l → {, T_r → }, T_a → ->,
T_s → ;.

```
C → T_c T_l L T_r
L → P T_a V T_s | R L
R → P T_a V T_s
```

## 4. Bodies of length two

Every body longer than two is split with new variables, from left to right. The
body *P T_a V T_s*, shared by *L* and *R*, is split once.

```
C   → T_c X₁          X₁ → T_l X₂          X₂ → L T_r
L   → P Y₁ | R L      R  → P Y₁
Y₁  → T_a Y₂          Y₂ → V T_s
P   → FULL_STACK_DEVELOPER | MACHINE_LEARNING_ENGINEER | FRONTEND_DEVELOPER
    | DATA_ENGINEER | UNQUALIFIED
V   → ACCEPTED | REJECTED
T_c → classification    T_l → {    T_r → }    T_a → ->    T_s → ;
```

This is the grammar in CNF: 20 productions over the variables
{C, X₁, X₂, L, R, Y₁, Y₂, P, V, T_c, T_l, T_r, T_a, T_s}, every one of the form
A → BC or A → a.

## Example derivation

For w = `classification { FULL_STACK_DEVELOPER -> ACCEPTED ; }` (7 tokens), the
leftmost derivation in CNF takes 2·7 − 1 = 13 steps, as every derivation of a
string of length *n* in CNF does (*n* − 1 binary steps and *n* terminal steps):

```
C ⇒ T_c X₁ ⇒ classification X₁ ⇒ classification T_l X₂ ⇒ classification { X₂
  ⇒ classification { L T_r ⇒ classification { P Y₁ T_r
  ⇒ classification { FULL_STACK_DEVELOPER Y₁ T_r
  ⇒ classification { FULL_STACK_DEVELOPER T_a Y₂ T_r
  ⇒ classification { FULL_STACK_DEVELOPER -> Y₂ T_r
  ⇒ classification { FULL_STACK_DEVELOPER -> V T_s T_r
  ⇒ classification { FULL_STACK_DEVELOPER -> ACCEPTED T_s T_r
  ⇒ classification { FULL_STACK_DEVELOPER -> ACCEPTED ; T_r
  ⇒ classification { FULL_STACK_DEVELOPER -> ACCEPTED ; }
```

Its derivation tree is binary: every internal node has two children, or one leaf.

## Membership with CYK

pyformlang decides membership with the CYK algorithm (`CFG.contains`), which runs
on the CNF. In the test, the tokens are written as lowercase names (`lbrace` for
`{`, `arrow` for `->`, …) because pyformlang reads capitalized words as variables:

```python
from pyformlang.cfg import CFG, Variable

cnf = CFG.from_text(CNF_TEXT, start_symbol=Variable("C"))
cnf.is_normal_form()                    # True
cnf.contains(["classification", "lbrace", "full_stack_developer", "arrow",
              "accepted", "semicolon", "rbrace"])     # True
cnf.contains(["classification", "lbrace", "rbrace"])  # False: one result at least
```

`tests/test_normal_form.py` checks that:

- the grammar of step 4 is in CNF and the grammar of step 1 is not;
- both accept every classification block of one or two results (110 strings), and
  reject every string obtained by deleting one token from them (1170 strings);
- the CNF obtained by pyformlang's own conversion (`to_normal_form`) accepts the
  same strings;
- the CNF accepts the classification blocks of `examples/resume_01..03.resume`.
