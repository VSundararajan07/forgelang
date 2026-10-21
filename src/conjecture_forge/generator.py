from itertools import combinations
from .graph import Graph

def graph_count(n):
    if n < 0: raise ValueError("n must be non-negative")
    return 1 << (n * (n - 1) // 2)

def generate_graphs(n):
    """Yield every labelled simple graph on n vertices."""
    if n < 0: raise ValueError("n must be non-negative")
    possible = tuple(combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        yield Graph(n, frozenset(possible[i] for i in range(len(possible))
                                 if mask & (1 << i)))

def estimate_total_graphs(max_vertices, min_vertices=1):
    return sum(graph_count(n) for n in range(min_vertices, max_vertices + 1))
