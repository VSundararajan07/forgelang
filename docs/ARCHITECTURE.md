# Architecture

`graph.py` implements immutable simple graphs and graph predicates. `generator.py` enumerates labelled graphs. `conjectures.py` models an implication P(G) => Q(G). `search.py` evaluates candidates. `minimize.py` greedily deletes vertices/edges while retaining counterexample status. `certificate.py` writes and independently rechecks JSON certificates. `cli.py` exposes the tool.

The certificate is a reproducible record, not a formal proof in a theorem prover.
