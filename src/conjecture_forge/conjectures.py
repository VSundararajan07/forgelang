from dataclasses import dataclass
from .graph import Graph

@dataclass(frozen=True)
class Conjecture:
    name: str
    statement: str
    premise: object
    conclusion: object

    def is_counterexample(self, graph: Graph) -> bool:
        return bool(self.premise(graph)) and not bool(self.conclusion(graph))

def min_degree_at_least(graph, k):
    return graph.n > 0 and all(d >= k for d in graph.degrees())

def hamiltonicity_conjecture():
    return Conjecture(
        "min-degree-two-implies-hamiltonian",
        "Every connected simple graph with minimum degree at least 2 has a Hamiltonian cycle.",
        lambda g: g.is_connected() and min_degree_at_least(g, 2),
        lambda g: g.has_hamiltonian_cycle())

def connected_perfect_matching_conjecture():
    return Conjecture(
        "connected-implies-perfect-matching",
        "Every connected simple graph with at least two vertices has a perfect matching.",
        lambda g: g.n >= 2 and g.is_connected(),
        lambda g: g.has_perfect_matching())

def tree_perfect_matching_conjecture():
    def is_tree(g):
        return (
            g.n >= 2
            and g.is_connected()
            and len(g.edges) == g.n - 1
        )

    return Conjecture(
        "tree-implies-perfect-matching",
        "Every tree with at least two vertices has a perfect matching.",
        is_tree,
        lambda g: g.has_perfect_matching()
    )

def built_in_conjectures():
    cs = [
        hamiltonicity_conjecture(),
        connected_perfect_matching_conjecture(),
        tree_perfect_matching_conjecture()
    ]
    return {c.name: c for c in cs}
