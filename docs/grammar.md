# Grammar

EBNF specification of the ResumeLens candidate profile language, implemented with textX in [`grammar/resume.tx`](../grammar/resume.tx).

## Terminals

- `STRING` — quoted text, e.g. `"Wednesday Addams"`
- `EMAIL` — email address, e.g. `wednesday@nevermore.edu`
- `PHONE` — phone number, e.g. `+1 212 555 0134`
- `URL` — `http(s)://...` link
- `DATE` — `YYYY-MM` or `YYYY-MM-DD`
- `CANON` — canonical skill token, uppercase identifier, e.g. `JAVASCRIPT`, `NODE_JS`
- Keywords: `"candidate"` `"headline"` `"location"` `"summary"` `"contact"` `"email"` `"phone"` `"linkedin"` `"skills"` `"languages"` `"native"` `"full_professional"` `"professional"` `"basic"` `"experience"` `"role"` `"at"` `"in"` `"from"` `"to"` `"present"` `"education"` `"classification"` `"FULL_STACK_DEVELOPER"` `"MACHINE_LEARNING_ENGINEER"` `"FRONTEND_DEVELOPER"` `"DATA_ENGINEER"` `"ACCEPTED"` `"REJECTED"`

## Non-terminals

`CandidateProfile`, `Header`, `Contact`, `Skills`, `Qualification`, `Languages`, `Language`, `Level`, `Experiences`, `Experience`, `Task`, `Period`, `Education`, `Degree`, `Classification`, `Result`, `Profile`, `Verdict`

## EBNF rules

```
CandidateProfile ::= "candidate" STRING "{" Header Contact Skills [Languages]
                     Experiences Education Classification "}" ;

Header           ::= "headline" ":" STRING ";"
                     "location" ":" STRING ";"
                     [ "summary" ":" STRING ";" ] ;

Contact          ::= "contact" "{" [ "email" ":" EMAIL ";" ]
                                   [ "phone" ":" PHONE ";" ]
                                   [ "linkedin" ":" URL ";" ] "}" ;

Skills           ::= "skills" "{" Qualification { "," Qualification } "}" ;
Qualification    ::= CANON ;

Languages        ::= "languages" "{" Language { Language } "}" ;
Language         ::= STRING ":" Level ";" ;
Level            ::= "native" | "full_professional" | "professional" | "basic" ;

Experiences      ::= "experience" "{" Experience { Experience } "}" ;
Experience       ::= "role" STRING "at" STRING Period [ "in" STRING ]
                     [ "{" Task { Task } "}" ] ;
Task             ::= "-" STRING ;
Period           ::= "from" DATE "to" ( DATE | "present" ) ;

Education        ::= "education" "{" Degree { Degree } "}" ;
Degree           ::= STRING "at" STRING Period ";" ;

Classification   ::= "classification" "{" Result { Result } "}" ;
Result           ::= Profile "->" Verdict ";" ;
Profile          ::= "FULL_STACK_DEVELOPER" | "MACHINE_LEARNING_ENGINEER"
                   | "FRONTEND_DEVELOPER" | "DATA_ENGINEER" ;
Verdict          ::= "ACCEPTED" | "REJECTED" ;
```
