# Grammar Specification

EBNF specification of the ResumeLens candidate profile language, implemented with textX in [`grammar/resume.tx`](../grammar/resume.tx).

## Terminals

- `STRING` — Quoted text, e.g. `"Wednesday Addams"`
- `EMAIL` — Email address, e.g. `wednesday@nevermore.edu`
- `PHONE` — Phone number, e.g. `+1 212 555 0134`
- `URL` — `http(s)://...` web link
- `DATE` — `YYYY-MM` or `YYYY-MM-DD`, with month `01`–`12` and day `01`–`31`
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
  classified once, `UNQUALIFIED` never accepted together with a profile, and
  every verdict equal to the one its stage-3 automaton gives for the skills.

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

The Chomsky Normal Form of the `classification` part of this grammar (RAA3) is
derived step by step in [`normal_forms.md`](normal_forms.md).
