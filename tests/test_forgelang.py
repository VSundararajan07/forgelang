import pytest

from conjecture_forge.forgelang import (
    ForgeLangSemanticError,
    ForgeLangSyntaxError,
    parse_forgelang,
    to_conjecture,
)
from conjecture_forge.graph import Graph


def parse(body):
    return parse_forgelang('conjecture "Test":\n    V(G in SimpleGraphs: ' + body + ')\n')


def holds(body, graph):
    return to_conjecture(parse(body)).conclusion(graph)


def test_comparison_and_arithmetic():
    g = Graph.from_edges(3, [(0, 1), (1, 2)])
    assert holds("vertices(G) == 3 & edges(G) == vertices(G) - 1", g)
    assert holds("vertices(G) >= 3 | edges(G) == 0", g)


def test_implication_and_biconditional_semantics():
    path3 = Graph.from_edges(3, [(0, 1), (1, 2)])
    assert holds("(tree(G) => connected(G))", path3)
    assert holds("tree(G) <=> (connected(G) & edges(G) == vertices(G) - 1)", path3)
    assert not holds("tree(G) <=> hamiltonian(G)", path3)


def test_negation_and_graph_functions():
    triangle = Graph.from_edges(3, [(0, 1), (1, 2), (0, 2)])
    assert holds("!bipartite(G) & has_odd_cycle(G)", triangle)
    assert holds("hamiltonian(G)", triangle)


def test_vertex_universal_and_existential_quantifiers():
    path3 = Graph.from_edges(3, [(0, 1), (1, 2)])
    assert holds("V(v in Vertices(G): degree(G, v) >= 1)", path3)
    assert holds("E(v in Vertices(G): degree(G, v) == 2)", path3)
    assert not holds("V(v in Vertices(G): degree(G, v) >= 2)", path3)


def test_invalid_syntax_has_diagnostic():
    with pytest.raises(ForgeLangSyntaxError):
        parse_forgelang('conjecture "Bad": V(G in SimpleGraphs connected(G))')


def test_unknown_function_rejected():
    with pytest.raises(ForgeLangSemanticError, match="Unknown ForgeLang function"):
        parse("magic(G)")


def test_unknown_variable_rejected():
    with pytest.raises(ForgeLangSemanticError, match="Unknown variable"):
        parse("degree(G, x) >= 0")


def test_top_level_existential_graph_claim_not_supported_yet():
    with pytest.raises(ForgeLangSemanticError, match="must start with V"):
        parse_forgelang('conjecture "Exists": E(G in SimpleGraphs: vertices(G) > 0)')
