# ForgeLang v0.1

ForgeLang is a small, safe domain-specific language for expressing graph-theory conjectures and checking finite graph cases.

## Run a conjecture

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

From the repository root:

```powershell
python main.py check examples/minimum_degree_hamiltonian.forge --max-vertices 5
```

The command searches labelled simple graphs within the requested bounds. Finding a counterexample disproves the claim. Not finding one is **not a proof**.

## Declaration and quantifiers

Every v0.1 conjecture is a universal claim over finite simple graphs:

```text
conjecture "Name":
    V(G in SimpleGraphs: <boolean expression>)
```

Inside the graph expression, quantification over its vertices is supported:

```text
V(v in Vertices(G): degree(G, v) >= 0)
E(v in Vertices(G): degree(G, v) >= 1)
```

`V` means universal quantification; `E` means existential quantification. Empty vertex domains follow standard logic: a universal statement over an empty set is true, and an existential statement over an empty set is false.

Top-level existential graph conjectures, quantification over graph collections inside formulas, and quantification over sets of edges/matchings are not implemented in v0.1.

## Operators and precedence

From highest to lowest:

1. Function calls, parentheses, and arithmetic (`*`, `/` before `+`, `-`).
2. Comparisons: `==`, `!=`, `>`, `<`, `>=`, `<=`.
3. Negation: `!`.
4. Conjunction: `&`.
5. Disjunction: `|`.
6. Implication: `=>` (right-associative).
7. Biconditional: `<=>` (use parentheses when chaining).

Examples:

```text
P & Q
P | Q
!P
P => Q
P <=> Q
edges(G) == vertices(G) - 1
```

## Built-in graph functions

- `vertices(G)` — number of vertices.
- `edges(G)` — number of edges.
- `degree(G, v)` — degree of vertex `v`.
- `min_degree(G)` — minimum degree, defined as `0` for an empty graph.
- `max_degree(G)` — maximum degree, defined as `0` for an empty graph.
- `connected(G)` — whether the graph is connected (`False` for the empty graph).
- `tree(G)` — whether the graph is a connected tree with at least one vertex.
- `bipartite(G)` — whether the graph is bipartite.
- `has_odd_cycle(G)` — whether the graph is non-bipartite.
- `hamiltonian(G)` — whether the graph has a Hamiltonian cycle.
- `has_perfect_matching(G)` — whether the graph has a perfect matching.

Functions are explicitly registered; ForgeLang source is never executed as Python. Unknown functions, unknown variables, unsupported quantifier domains, and invalid arguments produce diagnostics.

## Current limitations

- The parser is implemented with Lark and the evaluator uses a restricted AST.
- v0.1 accepts one top-level `V(G in SimpleGraphs: ...)` conjecture per file.
- Nested vertex quantifiers are evaluated for each candidate graph.
- Integer division is accepted only when it has an integer result; division by zero is rejected.
- This is bounded counterexample search, not a general theorem prover.
- Syntax and semantic diagnostics are intended to be helpful, but the language is still an early version.
