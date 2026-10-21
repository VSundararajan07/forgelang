# Complexity

Let n be vertices and m edges.

- Degree calculation: O(n+m).
- Connectivity: O(n+m).
- Exhaustive graph count at fixed n: 2^(n(n-1)/2).
- Hamiltonian cycle backtracking: O(n!) worst case.
- Perfect matching backtracking: exponential worst case.
- Minimization: multiple passes over up to n+m deletions; each candidate reruns property predicates.

These are worst-case bounds; actual time depends on the conjecture and graph family.
