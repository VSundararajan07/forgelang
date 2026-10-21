# Implementation status

- [x] Graph representation and graph properties
- [x] Labelled graph enumeration
- [x] Two built-in conjectures
- [x] Counterexample search and greedy minimization
- [x] JSON certificate writing and verification
- [x] CLI, tests, benchmark starter, documentation

Limitations: exhaustive enumeration only scales to small graphs; isomorphic graphs are repeated; minimization is greedy; arbitrary conjectures are Python predicates rather than a safe user-defined formula language.

Next: run tests, add property-guided graph generation, and investigate isomorph-free enumeration or SAT/SMT backends.
