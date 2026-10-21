from dataclasses import dataclass
from itertools import combinations

@dataclass(frozen=True)
class Graph:
    """Simple undirected graph with vertices 0..n-1."""
    n: int
    edges: frozenset[tuple[int, int]]

    def __post_init__(self):
        if self.n < 0:
            raise ValueError("n must be non-negative")
        norm = set()
        for u, v in self.edges:
            if not (0 <= u < self.n and 0 <= v < self.n):
                raise ValueError("edge endpoint outside graph")
            if u == v:
                raise ValueError("self-loops are not allowed")
            norm.add((min(u, v), max(u, v)))
        object.__setattr__(self, "edges", frozenset(norm))

    @classmethod
    def from_edges(cls, n, edges):
        return cls(n, frozenset(tuple(e) for e in edges))

    def adjacency(self):
        adj = [set() for _ in range(self.n)]
        for u, v in self.edges:
            adj[u].add(v); adj[v].add(u)
        return adj

    def degrees(self):
        d = [0] * self.n
        for u, v in self.edges:
            d[u] += 1; d[v] += 1
        return tuple(d)

    def is_connected(self):
        if self.n == 0:
            return False
        adj, seen, stack = self.adjacency(), {0}, [0]
        while stack:
            u = stack.pop()
            for v in adj[u] - seen:
                seen.add(v); stack.append(v)
        return len(seen) == self.n

    def has_hamiltonian_cycle(self):
        if self.n < 3:
            return False
        adj, path, used = self.adjacency(), [0], {0}
        def visit(u):
            if len(path) == self.n:
                return 0 in adj[u]
            for v in sorted(adj[u]):
                if v not in used and v > 0:
                    used.add(v); path.append(v)
                    if visit(v): return True
                    path.pop(); used.remove(v)
            return False
        return visit(0)

    def has_perfect_matching(self):
        if self.n == 0: return True
        if self.n % 2: return False
        adj, full = self.adjacency(), (1 << self.n) - 1
        def visit(mask):
            if mask == full: return True
            u = next(i for i in range(self.n) if not (mask & (1 << i)))
            for v in adj[u]:
                if not (mask & (1 << v)):
                    if visit(mask | (1 << u) | (1 << v)): return True
            return False
        return visit(0)

    def without_edge(self, edge):
        u, v = edge
        return Graph(self.n, self.edges - {(min(u, v), max(u, v))})

    def without_vertex(self, vertex):
        if not 0 <= vertex < self.n: raise ValueError("vertex out of range")
        remap = {i: i if i < vertex else i - 1 for i in range(self.n) if i != vertex}
        edges = [(remap[u], remap[v]) for u, v in self.edges if vertex not in (u, v)]
        return Graph(self.n - 1, frozenset(edges))

    def to_dict(self):
        return {"n": self.n, "edges": [list(e) for e in sorted(self.edges)]}

    @classmethod
    def from_dict(cls, data):
        return cls.from_edges(int(data["n"]), data["edges"])
