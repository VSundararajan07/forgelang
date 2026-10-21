# Algorithms

- Exhaustive generation: each of the n(n-1)/2 possible edges is either present or absent, giving 2^(n choose 2) labelled graphs.
- Connectivity: DFS in O(n+m).
- Hamiltonian cycle: backtracking, factorial worst-case time.
- Perfect matching: recursive pairing search, exponential worst-case time.
- Minimization: repeatedly test single vertex/edge deletions until none preserves the counterexample. This is local, not global, minimality.
