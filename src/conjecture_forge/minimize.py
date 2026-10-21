def minimize_counterexample(graph, conjecture):
    """Greedily delete vertices/edges while preserving counterexample status."""
    if not conjecture.is_counterexample(graph):
        raise ValueError("input graph is not a counterexample")
    current, changed = graph, True
    while changed:
        changed = False
        for v in range(current.n):
            candidate = current.without_vertex(v)
            if conjecture.is_counterexample(candidate):
                current, changed = candidate, True
                break
        if changed: continue
        for edge in sorted(current.edges):
            candidate = current.without_edge(edge)
            if conjecture.is_counterexample(candidate):
                current, changed = candidate, True
                break
    return current
