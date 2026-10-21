# Conjecture Forge

A pure-Python research prototype for searching small simple graphs for counterexamples to graph-theoretic conjectures.

A conjecture is represented as an implication `P(G) => Q(G)`. A counterexample is a graph for which `P(G)` is true and `Q(G)` is false.

## Quick start (Python 3.10+)

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -e .[dev]
python main.py list
python main.py search min-degree-two-implies-hamiltonian --max-vertices 5
python main.py verify output/counterexample.json
python -m pytest
```

## Built-in false claims
- `min-degree-two-implies-hamiltonian`: every connected simple graph with minimum degree at least 2 has a Hamiltonian cycle.
- `connected-implies-perfect-matching`: every connected simple graph with at least 2 vertices has a perfect matching.

Both are false; the program should find counterexamples.

## Research limitations
There are `2^(n(n-1)/2)` labelled simple graphs on `n` vertices, so exhaustive enumeration grows extremely quickly. Isomorphic graphs may be examined more than once. The minimizer is greedy and returns a graph locally minimal under single vertex/edge deletions, not necessarily a globally smallest graph. Not finding a counterexample within a finite search bound is not a proof.

## Add a conjecture
Construct `Conjecture(name, statement, premise, conclusion)` with two deterministic predicates over `Graph`. Keep predicates side-effect-free.

## Project structure
`src/conjecture_forge/` contains graph representation, generation, conjecture definitions, search, minimization, certificates, and CLI. `tests/`, `benchmarks/`, and `docs/` contain quality and research materials.

MIT licensed; see `LICENSE`.

## ForgeLang (early version)

ForgeLang lets you write graph conjectures using symbolic logic. See
[`docs/FORGELANG.md`](docs/FORGELANG.md) and the `.forge` examples in `examples/`.

Install the project and its dependencies, then run a conjecture:

```powershell
python -m pip install -e .
python main.py check examples/minimum_degree_hamiltonian.forge --max-vertices 5
```

The engine searches a finite range of graphs. Finding a counterexample disproves
the conjecture; finding none within the selected bounds is not a proof.

## ForgeLang Web Interface

A local browser interface is included. Install the project dependencies and start it from the repository root:

```bash
python -m pip install -e .
python webapp.py
```

Then open <http://127.0.0.1:5000>. Enter a ForgeLang conjecture in the editor, choose the vertex bound and graph-search limit, and click **Check conjecture**. The interface shows the search status, graphs examined, runtime, and a drawing of a minimized counterexample when one is found.

The web interface is intended for local development. It binds to `127.0.0.1` by default. A finite search that finds no counterexample is not a proof. Graph enumeration grows exponentially, so use small bounds while experimenting.
