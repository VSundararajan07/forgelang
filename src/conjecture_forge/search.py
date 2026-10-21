
from dataclasses import dataclass
from time import perf_counter

from .generator import generate_graphs, estimate_total_graphs
from .minimize import minimize_counterexample



@dataclass
class SearchResult:
    graph: object
    examined: int
    elapsed: float
    total_graphs: int

    @property
    def found(self):
        return self.graph is not None

    @property
    def counterexample(self):
        return self.graph



def search_counterexample(
    conjecture,
    max_vertices=5,
    minimize=True,
):
    start = perf_counter()
    examined = 0
    total_graphs = estimate_total_graphs(max_vertices)

    for n in range(1, max_vertices + 1):
        for graph in generate_graphs(n):
            examined += 1

            if conjecture.is_counterexample(graph):
                if minimize:
                    graph = minimize_counterexample(
                        graph, conjecture
                    )

                return SearchResult(
                    graph=graph,
                    examined=examined,
                    elapsed=perf_counter() - start,
                    total_graphs=total_graphs,
                )

    return SearchResult(
        graph=None,
        examined=examined,
        elapsed=perf_counter() - start,
        total_graphs=total_graphs,
    )


def search_conjecture(
    conjecture,
    max_vertices=5,
    minimize=True,
):
    """Backward-compatible wrapper for existing tests."""
    return search_counterexample(
        conjecture,
        max_vertices=max_vertices,
        minimize=minimize,
    )
