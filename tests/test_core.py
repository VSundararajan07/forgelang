from conjecture_forge.graph import Graph
from conjecture_forge.generator import graph_count, generate_graphs
from conjecture_forge.conjectures import hamiltonicity_conjecture, connected_perfect_matching_conjecture
from conjecture_forge.search import search_conjecture
from conjecture_forge.minimize import minimize_counterexample
from conjecture_forge.certificate import write_certificate, verify_certificate

def test_graph_basics():
    g = Graph.from_edges(3, [(0, 1), (1, 2)])
    assert g.degrees() == (1, 2, 1)
    assert g.is_connected()
    assert not g.has_hamiltonian_cycle()
    assert not g.has_perfect_matching()

def test_graph_generation_counts():
    assert graph_count(3) == 8
    assert len(list(generate_graphs(4))) == 64

def test_search_and_minimize():
    c = hamiltonicity_conjecture()
    result = search_conjecture(c, max_vertices=5)
    assert result.found and c.is_counterexample(result.counterexample)
    minimized = minimize_counterexample(result.counterexample, c)
    assert c.is_counterexample(minimized)
    assert all(not c.is_counterexample(minimized.without_vertex(v)) for v in range(minimized.n))
    assert all(not c.is_counterexample(minimized.without_edge(e)) for e in minimized.edges)

def test_matching_conjecture():
    c = connected_perfect_matching_conjecture()
    assert search_conjecture(c, max_vertices=3).found

def test_certificate(tmp_path):
    c = hamiltonicity_conjecture()
    graph = search_conjecture(c, max_vertices=5).counterexample
    p = tmp_path / "certificate.json"
    write_certificate(graph, c, p)
    assert verify_certificate(p, c)[0]
