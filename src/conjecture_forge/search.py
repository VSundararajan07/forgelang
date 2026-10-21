from dataclasses import dataclass
from time import perf_counter
from .generator import generate_graphs

@dataclass
class SearchResult:
    conjecture_name: str
    max_vertices: int
    graphs_examined: int
    elapsed_seconds: float
    counterexample: object = None

    @property
    def found(self):
        return self.counterexample is not None

def search_conjecture(conjecture, max_vertices=5, min_vertices=1, max_graphs=None):
    if min_vertices < 0 or max_vertices < min_vertices:
        raise ValueError("invalid vertex bounds")
    start, examined = perf_counter(), 0
    for n in range(min_vertices, max_vertices + 1):
        for graph in generate_graphs(n):
            if max_graphs is not None and examined >= max_graphs:
                return SearchResult(conjecture.name, max_vertices, examined,
                                    perf_counter() - start)
            examined += 1
            if conjecture.is_counterexample(graph):
                return SearchResult(conjecture.name, max_vertices, examined,
                                    perf_counter() - start, graph)
    return SearchResult(conjecture.name, max_vertices, examined, perf_counter() - start)
