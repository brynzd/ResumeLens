# Grammar Specification

The candidate profile language of ResumeLens: its domain, the EBNF specification
implemented with textX in [`grammar/resume.tx`](../grammar/resume.tx), and the Chomsky
Normal Form of part of the grammar. The metamodel is in [`metamodel.md`](metamodel.md).

## Domain

The DSL represents the output of ResumeLens: what the pipeline learned about one
candidate. It is not an input format for raw résumés, and it records the results of
extraction, normalization and recognition, not how they work. A LinkedIn-style profile
was the reference layout.

| Concept | Meaning | Comes from |
|---|---|---|
| Candidate | the root: one document describes one candidate, identified by name | stage 1 |
| Header | headline, location and an optional summary; the automata do not evaluate it | stage 1 |
| Contact | email, phone and LinkedIn; each one is optional, but at least one is needed | stage 1 |
| Skill | a canonical token of the transducer, without duplicates: `REACT`, never `React.js` | stage 2 |
| Language | a spoken language and its level: `native`, `full_professional`, `professional` or `basic` | stage 1 |
| Experience | role, company, period, an optional location and tasks | stage 1 |
| Degree | degree, institution and period | stage 1 |
| Period | a start date, and an end date or `present`; dates are `YYYY-MM` or `YYYY-MM-DD` | stage 1 |
| Classification | one result (profile, verdict) per profile, and `UNQUALIFIED` when no profile is accepted | stage 3 |

A verdict is a formal statement about the pattern of a profile, never a hiring
recommendation. A mandatory concept the résumé does not provide is not invented: the
document leaves it empty and the grammar rejects it as incomplete. Outside the domain:
raw skill strings, scores or rankings, skills not written in the résumé, and free
sections such as certifications or hobbies.

## Terminals

- `STRING` — Quoted text, e.g. `"Wednesday Addams"`
- `EMAIL` — Email address, e.g. `wednesday@nevermore.edu`
- `PHONE` — Phone number, e.g. `+1 212 555 0134`
- `URL` — `http(s)://...` web link
- `DATE` — `YYYY-MM` or `YYYY-MM-DD`, with month `01`–`12` and day `01`–`31`; it may not be followed by a hyphen or a digit, so `2018-08-32` is an invalid DATE
- `CANON` — Canonical skill token, uppercase identifier ($\Gamma$), e.g. `JAVASCRIPT`, `NODE_JS`, `PYTHON`
- **Keywords:** `"candidate"` `"headline"` `"location"` `"summary"` `"contact"` `"email"` `"phone"` `"linkedin"` `"skills"` `"languages"` `"native"` `"full_professional"` `"professional"` `"basic"` `"experience"` `"role"` `"at"` `"in"` `"from"` `"to"` `"present"` `"education"` `"classification"` `"FULL_STACK_DEVELOPER"` `"MACHINE_LEARNING_ENGINEER"` `"FRONTEND_DEVELOPER"` `"DATA_ENGINEER"` `"UNQUALIFIED"` `"ACCEPTED"` `"REJECTED"`

## Non-terminals

`CandidateProfile`, `Header`, `Contact`, `Skills`, `Qualification`, `Languages`, `Language`, `Level`, `Experiences`, `Experience`, `Task`, `Period`, `EndDate`, `Education`, `Degree`, `Classification`, `Result`, `Profile`, `Verdict`

## EBNF rules

```ebnf
CandidateProfile ::= "candidate" STRING "{" 
                        Header 
                        Contact 
                        Skills 
                        [ Languages ] 
                        Experiences 
                        Education 
                        Classification 
                     "}" ;

Header           ::= "headline" ":" STRING ";"
                     "location" ":" STRING ";"
                     [ "summary" ":" STRING ";" ] ;

Contact          ::= "contact" "{" 
                         [ "email" ":" EMAIL ";" ]
                         [ "phone" ":" PHONE ";" ]
                         [ "linkedin" ":" URL ";" ] 
                     "}" ;

Skills           ::= "skills" "{" Qualification { "," Qualification } "}" ;

Qualification    ::= CANON ;

Languages        ::= "languages" "{" Language { Language } "}" ;

Language         ::= STRING ":" Level ";" ;

Level            ::= "native" | "full_professional" | "professional" | "basic" ;

Experiences      ::= "experience" "{" Experience { Experience } "}" ;

Experience       ::= "role" STRING "at" STRING Period [ "in" STRING ]
                     [ "{" Task { Task } "}" ] ;

Task             ::= "-" STRING ;

Period           ::= "from" DATE "to" EndDate ;

EndDate          ::= DATE | "present" ;

Education        ::= "education" "{" Degree { Degree } "}" ;

Degree           ::= STRING "at" STRING Period ";" ;

Classification   ::= "classification" "{" Result { Result } "}" ;

Result           ::= Profile "->" Verdict ";" ;

Profile          ::= "FULL_STACK_DEVELOPER" 
                   | "MACHINE_LEARNING_ENGINEER"
                   | "FRONTEND_DEVELOPER" 
                   | "DATA_ENGINEER"
                   | "UNQUALIFIED" ;

Verdict          ::= "ACCEPTED" | "REJECTED" ;
```

## Structural characteristics

- **One root, fixed order.** A document describes exactly one candidate: the
  `candidate` block contains its sections in a fixed sequence (header, contact,
  skills, languages, experience, education, classification). A section out of
  order is a syntax error (`tests/invalid/syn_wrong_section_order.resume`).
- **Optional parts.** `[ … ]` marks the parts a résumé may omit: the summary,
  each contact field and the whole `languages` section.
- **Repetition.** `{ … }` after a first occurrence means *one or more*: skills,
  languages, experiences, tasks, degrees and classification results. Skills are
  **separated** by commas (`A, B, C`, no trailing comma), while languages,
  degrees, results and the header and contact fields are **terminated** by `;`.
- **Bounded nesting.** Blocks are delimited by `{ … }` and nest at most three
  levels: candidate → section → experience → tasks. There is no recursive rule,
  so the nesting depth of a document is fixed by the grammar.
- **Closed vocabularies.** `Level`, `Profile` and `Verdict` are alternatives of
  keywords, so the parser itself rejects an unknown profile or verdict, and
  `EndDate` is a date or the keyword `present`.
- **Lexical layer.** The terminals `EMAIL`, `PHONE`, `URL`, `DATE` and `CANON`
  are regular expressions (textX match rules) that constrain the shape of the
  text; `STRING` is a quoted string. `//` and `/* … */` comments are ignored
  anywhere.
- **Semantic layer.** What a context-free grammar cannot express is checked on
  the parsed model by [`src/validator.py`](../src/validator.py): non-empty name,
  headline and location; at least one contact field; periods that do not end
  before they start; unique skills from the canonical vocabulary; each profile
  classified once; and every verdict, `UNQUALIFIED` included, equal to the one
  the stage-3 automata give for the skills.

## From EBNF to textX

| EBNF | textX (`grammar/resume.tx`) | Meaning |
|---|---|---|
| `A B` | `A B` | sequence |
| `A \| B` | `A \| B` | alternative (ordered choice: textX parses with a PEG) |
| `[ A ]` | `A?` or `( … )?` | optional |
| `A { A }` | `items+=A` | one or more |
| `A { "," A }` | `items+=A[',']` | one or more, separated by commas |
| `Rule ::= …` | `Rule: … ;` | a rule; an assignment such as `name=STRING` becomes an attribute of the metamodel class |
| terminal | match rule (`DATE: /…/;`) or string literal (`'skills'`) | lexical element |

## Chomsky Normal Form of the classification rules

Learning outcome RAA3 asks to simplify grammars with normal forms. textX does not need
a normal form: it parses with a PEG, a recursive-descent parser with ordered choice. The
**Chomsky Normal Form (CNF)** is the form the CYK membership algorithm requires, and
converting the `classification` rules of the grammar shows every simplification step.

A context-free grammar is in CNF when every production has the form **A → BC** (two
variables) or **A → a** (one terminal); λ may only be produced by the start symbol,
and only if the start symbol does not appear on any right-hand side.

### 1. From EBNF to a context-free grammar

The fragment is made of the rules `Classification`, `Result`, `Profile` and `Verdict`.
Its terminals are `classification`, `{`, `}`, `->`, `;`, the five profiles and the two
verdicts. EBNF repetition is not a production of a CFG, so `Result { Result }` (one or
more results) becomes a new variable *L* with a right-recursive rule:

G = (Σ, N, S, P) with N = {C, L, R, P, V}, S = C and the productions

```
C → classification { L }
L → R | R L
R → P -> V ;
P → FULL_STACK_DEVELOPER | MACHINE_LEARNING_ENGINEER | FRONTEND_DEVELOPER
  | DATA_ENGINEER | UNQUALIFIED
V → ACCEPTED | REJECTED
```

### 2. Simplification

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

### 3. Terminals in long bodies

In a body of two or more symbols every terminal is replaced by a new variable that
produces only that terminal: T_c → classification, T_l → {, T_r → }, T_a → ->,
T_s → ;.

```
C → T_c T_l L T_r
L → P T_a V T_s | R L
R → P T_a V T_s
```

### 4. Bodies of length two

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

### Example derivation

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

### Membership with CYK

pyformlang decides membership with the CYK algorithm (`CFG.contains`), which runs
on the CNF. The tokens are written as lowercase names (`lbrace` for `{`, `arrow`
for `->`, …) because pyformlang reads capitalized words as variables:

```python
from pyformlang.cfg import CFG, Variable

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
P -> full_stack_developer | machine_learning_engineer | frontend_developer | data_engineer | unqualified
V -> accepted | rejected
"""
cnf = CFG.from_text(CNF, start_symbol=Variable("C"))
cnf.is_normal_form()                                  # True
cnf.contains(["classification", "lbrace", "full_stack_developer", "arrow",
              "accepted", "semicolon", "rbrace"])     # True
cnf.contains(["classification", "lbrace", "rbrace"])  # False: one result at least
```
