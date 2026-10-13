# Literature Review

The assignment asks for a review of the literature before implementing, to guide the
project, avoid redundancy and support the design decisions. This review covers the
problem (résumé screening as information extraction and normalization) and the four
formal models ResumeLens applies, and ends with the decisions each source supported.

## 1. Résumé screening and information extraction

Extracting structured data from résumés is a classic information-extraction task.
Yu, Guan and Zhou [24] proposed a cascaded approach: the résumé is first segmented
into general blocks (personal information, education, experience) and detailed
fields are then extracted inside each block with statistical models (HMM, SVM).
Statistical and neural parsers tolerate very different layouts, but their output is
hard to explain and they need annotated training data.

The same skill is written in many ways, so screening systems map mentions to a
controlled vocabulary. Public taxonomies such as ESCO [7] and O\*NET [22] describe
thousands of skills and occupations; ESCO, for example, gives every concept a
preferred label and alternative labels, the same idea as a canonical token and its
spellings.

Automated screening also raises fairness concerns: Raghavan et al. [17] review the
claims and practices of vendors of algorithmic pre-employment assessments and find
that how they validate their models and address bias is often not disclosed. This supports the scope of the
assignment: ResumeLens does not rank candidates or recommend hiring; it only states
whether the qualifications written in a résumé satisfy explicit, formally defined
patterns.

## 2. Regular expressions and finite automata

Kleene [13] introduced regular events and proved that they are exactly what finite
automata recognize; Thompson [21] compiled regular expressions into automata to
search text, a construction regex engines still use. Hopcroft, Motwani and Ullman [11]
and Sipser [20] give the constructions the project relies on: the 5-tuple of an
automaton, determinism, the equivalence of DFAs, NFAs and ε-NFAs, and the closure
properties of regular languages.

Python's `re` is a backtracking engine with extensions beyond regular languages, such
as backreferences [16]; Friedl [10] explains how its ordered alternation and
backtracking decide which match is found. The stage-1 patterns use no
backreferences, and their lookarounds only test a bounded context, so the languages
they describe remain regular.

## 3. Finite-state transducers in language processing

Finite-state transducers extend automata with an output and are a standard tool to
rewrite strings in natural-language processing. Mohri [15] studies sequential
(deterministic) transducers, whose output is produced in a single left-to-right pass,
and their determinization and minimization. Roche and Schabes [18] collect the
finite-state methods of language processing, Karttunen et al. [12] show how regular
expressions compile into automata and transducers for tokenization and normalization,
and Beesley and Karttunen [2] apply them to morphology, mapping surface forms to
canonical forms. Normalizing `React.js` to `REACT` is the same kind of mapping, from a
surface spelling to a canonical form.

## 4. Context-free grammars, normal forms and domain-specific languages

Chomsky [3] compared finite-state and phrase-structure models of language; his
1959 paper [4] classified grammars into the hierarchy that bears his name and showed
that every context-free language without λ can be generated with productions
A → BC and A → a, the Chomsky Normal Form. That is the form the CYK algorithm [23] needs to decide membership
in cubic time. Aho et al. [1] separate lexical, syntactic and semantic analysis, the
three levels at which the candidate documents are validated.

Ford [8] defined Parsing Expression Grammars (PEG), whose ordered choice removes the
ambiguity of alternatives; textX [6] builds on the PEG parser Arpeggio [5] and derives,
from a single grammar, both the parser and the metamodel (the classes of the parsed
model). Mernik, Heering and Sloane [14] describe when and how a domain-specific
language pays off, and Fowler [9] distinguishes external DSLs, with their own syntax
and parser, such as the ResumeLens candidate profile language.

## 5. Tools

pyformlang [19] is an educational Python library for formal languages: regular
expressions, finite automata, finite-state transducers and context-free grammars,
including the conversion to Chomsky Normal Form and CYK. ResumeLens uses it for the
transducer of stage 2, the automata of stage 3 and the verification of the normal
form. textX implements the DSL of stage 4.

## 6. How the review shaped ResumeLens

| Decision | Supported by |
|---|---|
| Rule-based extraction with one regular expression per type of information, instead of a trained model: deterministic and explainable, at the cost of layout conventions | [24] (the statistical alternative), [10], [11], [16] |
| Sections first, fields inside each section (positions, degrees, languages) | the cascaded segmentation of [24] |
| A canonical token per qualification with its alternative spellings | [7], [22] |
| A sequential (deterministic) transducer to normalize spellings | [12], [15] |
| One DFA per profile recognizing C₁⁺ C₂⁺ ⋯ Cₖ⁺, membership in linear time | [11], [13], [20] |
| An external DSL with a context-free grammar implemented in textX (PEG), validated at three levels | [1], [6], [8], [14] |
| The Chomsky Normal Form of part of the grammar and CYK membership (RAA3) | [4], [19], [23] |
| No ranking, no hiring recommendation: only explicit pattern membership | [17] |

### Gaps with respect to the state of the art

- Statistical and neural résumé parsers handle arbitrary layouts; ResumeLens needs
  section headers and `Title at Organization (start - end)` lines.
- Skill taxonomies have thousands of concepts; ResumeLens normalizes 23.
- Profiles are patterns of required categories; partial or weighted matching, as in
  ranking systems, is out of scope by design.

## References

1. A. V. Aho, M. S. Lam, R. Sethi, J. D. Ullman. *Compilers: Principles, Techniques, and Tools*, 2nd ed. Addison-Wesley, 2006.
2. K. R. Beesley, L. Karttunen. *Finite State Morphology*. CSLI Publications, 2003.
3. N. Chomsky. "Three models for the description of language." *IRE Transactions on Information Theory*, 2(3):113–124, 1956.
4. N. Chomsky. "On certain formal properties of grammars." *Information and Control*, 2(2):137–167, 1959.
5. I. Dejanović, G. Milosavljević, R. Vaderna. "Arpeggio: A flexible PEG parser for Python." *Knowledge-Based Systems*, 95:71–74, 2016.
6. I. Dejanović, R. Vaderna, G. Milosavljević, Ž. Vuković. "TextX: A Python tool for Domain-Specific Languages implementation." *Knowledge-Based Systems*, 115:1–4, 2017.
7. European Commission. *ESCO: European Skills, Competences, Qualifications and Occupations*. https://esco.ec.europa.eu
8. B. Ford. "Parsing expression grammars: a recognition-based syntactic foundation." In *Proceedings of the 31st ACM SIGPLAN-SIGACT Symposium on Principles of Programming Languages (POPL '04)*, pp. 111–122, 2004.
9. M. Fowler. *Domain-Specific Languages*. Addison-Wesley, 2010.
10. J. E. F. Friedl. *Mastering Regular Expressions*, 3rd ed. O'Reilly, 2006.
11. J. E. Hopcroft, R. Motwani, J. D. Ullman. *Introduction to Automata Theory, Languages, and Computation*, 3rd ed. Pearson, 2007.
12. L. Karttunen, J.-P. Chanod, G. Grefenstette, A. Schiller. "Regular expressions for language engineering." *Natural Language Engineering*, 2(4):305–328, 1996.
13. S. C. Kleene. "Representation of events in nerve nets and finite automata." In C. E. Shannon, J. McCarthy (eds.), *Automata Studies*, pp. 3–41. Princeton University Press, 1956.
14. M. Mernik, J. Heering, A. M. Sloane. "When and how to develop domain-specific languages." *ACM Computing Surveys*, 37(4):316–344, 2005.
15. M. Mohri. "Finite-state transducers in language and speech processing." *Computational Linguistics*, 23(2):269–311, 1997.
16. Python Software Foundation. "re — Regular expression operations." *The Python Standard Library*. https://docs.python.org/3/library/re.html
17. M. Raghavan, S. Barocas, J. Kleinberg, K. Levy. "Mitigating bias in algorithmic hiring: evaluating claims and practices." In *Proceedings of the 2020 Conference on Fairness, Accountability, and Transparency (FAT\* '20)*, pp. 469–481, 2020.
18. E. Roche, Y. Schabes (eds.). *Finite-State Language Processing*. MIT Press, 1997.
19. J. Romero. "Pyformlang: An educational library for formal language manipulation." In *Proceedings of the 52nd ACM Technical Symposium on Computer Science Education (SIGCSE '21)*, pp. 576–582, 2021.
20. M. Sipser. *Introduction to the Theory of Computation*, 3rd ed. Cengage Learning, 2013.
21. K. Thompson. "Regular expression search algorithm." *Communications of the ACM*, 11(6):419–422, 1968.
22. U.S. Department of Labor, Employment and Training Administration. *O\*NET OnLine*. https://www.onetonline.org
23. D. H. Younger. "Recognition and parsing of context-free languages in time n³." *Information and Control*, 10(2):189–208, 1967.
24. K. Yu, G. Guan, M. Zhou. "Resume information extraction with cascaded hybrid model." In *Proceedings of the 43rd Annual Meeting of the Association for Computational Linguistics (ACL '05)*, pp. 499–506, 2005.
