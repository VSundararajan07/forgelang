"""ForgeLang v0.1: a safe, small DSL for graph-theory conjectures.

Supported top-level form:
    conjecture "Name":
        V(G in SimpleGraphs: <boolean expression>)

Nested quantifiers over vertices are supported:
    V(v in Vertices(G): ...)
    E(v in Vertices(G): ...)

ForgeLang never evaluates user text as Python.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from lark import Lark, Transformer, UnexpectedInput, v_args

from .conjectures import Conjecture
from .graph import Graph


GRAMMAR = r"""
start: "conjecture" STRING ":" expr

?expr: biconditional
?biconditional: implication
              | implication "<=>" implication  -> iff
?implication: disjunction
            | disjunction "=>" implication    -> implies
?disjunction: conjunction
            | disjunction "|" conjunction     -> or_op
?conjunction: comparison
            | conjunction "&" comparison      -> and_op
?comparison: sum
           | sum COMP sum                     -> compare
?sum: product
    | sum "+" product                         -> add
    | sum "-" product                         -> subtract
?product: unary
        | product "*" unary                    -> multiply
        | product "/" unary                    -> divide
?unary: "!" unary                             -> not_op
      | "-" unary                              -> negate
      | atom
?atom: quantifier
     | function_call
     | NAME                                    -> variable
     | SIGNED_INT                              -> integer
     | "(" expr ")"
quantifier: QUANT "(" NAME IN domain ":" expr ")"
?domain: "SimpleGraphs"                        -> simple_graphs
       | "Vertices" "(" NAME ")"               -> vertices_domain
function_call: NAME "(" [arguments] ")"
arguments: expr ("," expr)*
COMP: "==" | "!=" | ">=" | "<=" | ">" | "<"
QUANT.2: "V" | "E"
IN.2: "in"
NAME: /[A-Za-z_][A-Za-z0-9_]*/
STRING: /"([^"\\\\]|\\\\.)*"/
%import common.SIGNED_INT
%import common.WS
%ignore WS
%ignore /#[^\n]*/
"""


class ForgeLangError(ValueError):
    """Base class for ForgeLang syntax and semantic errors."""


class ForgeLangSyntaxError(ForgeLangError):
    """Raised when a ForgeLang source file cannot be parsed."""


class ForgeLangSemanticError(ForgeLangError):
    """Raised when a parsed formula uses unsupported or invalid semantics."""


@v_args(inline=True)
class _BuildAst(Transformer):
    def start(self, string, expression):
        # JSON string decoding handles quotes and backslash escapes safely.
        import json
        return ("declaration", json.loads(str(string)), expression)

    def variable(self, name):
        return ("var", str(name))

    def integer(self, value):
        return ("int", int(value))

    def simple_graphs(self):
        return ("domain", "SimpleGraphs")

    def vertices_domain(self, name):
        return ("domain", "Vertices", str(name))

    def quantifier(self, quant, variable, _in, domain, expression):
        return ("quant", str(quant), str(variable), domain, expression)

    def function_call(self, name, args=None):
        if args is None:
            values = ()
        elif isinstance(args, tuple) and args and args[0] == "args":
            values = args[1]
        else:
            values = (args,)
        return ("call", str(name), values)

    def arguments(self, *values):
        return ("args", tuple(values))

    def not_op(self, value):
        return ("not", value)

    def negate(self, value):
        return ("neg", value)

    def and_op(self, left, right):
        return ("and", left, right)

    def or_op(self, left, right):
        return ("or", left, right)

    def implies(self, left, right):
        return ("implies", left, right)

    def iff(self, left, right):
        return ("iff", left, right)

    def compare(self, left, operator, right):
        return ("compare", str(operator), left, right)

    def add(self, left, right):
        return ("+", left, right)

    def subtract(self, left, right):
        return ("-", left, right)

    def multiply(self, left, right):
        return ("*", left, right)

    def divide(self, left, right):
        return ("/", left, right)


_PARSER = Lark(GRAMMAR, parser="lalr", transformer=_BuildAst())


@dataclass(frozen=True)
class ParsedConjecture:
    """Parsed conjecture source and its validated abstract syntax tree."""
    name: str
    expression: tuple
    source: str

    @property
    def statement(self) -> str:
        return self.source.strip()


def parse_forgelang(source: str) -> ParsedConjecture:
    """Parse a ForgeLang conjecture and validate its outer quantifier."""
    try:
        ast = _PARSER.parse(source)
    except UnexpectedInput as exc:
        context = exc.get_context(source, span=35).strip()
        raise ForgeLangSyntaxError(
            f"Syntax error at line {exc.line}, column {exc.column}:\n{context}"
        ) from None
    if not (isinstance(ast, tuple) and len(ast) == 3 and ast[0] == "declaration"):
        raise ForgeLangSyntaxError("Expected a conjecture declaration.")
    _, name, expression = ast
    if not (
        isinstance(expression, tuple)
        and len(expression) == 5
        and expression[0] == "quant"
        and expression[1] == "V"
        and expression[3] == ("domain", "SimpleGraphs")
    ):
        raise ForgeLangSemanticError(
            "A conjecture must start with V(G in SimpleGraphs: ...). "
            "Existential claims over all graphs are not yet supported as top-level claims."
        )
    if not isinstance(name, str) or not name.strip():
        raise ForgeLangSemanticError("Conjecture name cannot be empty.")
    _validate_expression(expression[4], bound_variables={expression[2]}, graph_variable=expression[2])
    return ParsedConjecture(name=name, expression=expression, source=source)


def _validate_expression(node: tuple, bound_variables: set[str], graph_variable: str) -> None:
    """Validate supported names, calls, domains, and variable bindings."""
    kind = node[0]
    if kind in {"int"}:
        return
    if kind == "var":
        if node[1] not in bound_variables:
            raise ForgeLangSemanticError(f"Unknown variable '{node[1]}'.")
        return
    if kind == "quant":
        _, quant, variable, domain, body = node
        if domain[1] == "SimpleGraphs":
            raise ForgeLangSemanticError(
                "Nested quantification over SimpleGraphs is not supported; "
                "quantify over vertices inside a graph instead."
            )
        if domain[1] != "Vertices" or domain[2] != graph_variable:
            raise ForgeLangSemanticError(
                "Vertex quantifiers must use Vertices(" + graph_variable + ")."
            )
        nested = set(bound_variables)
        nested.add(variable)
        _validate_expression(body, nested, graph_variable)
        return
    if kind == "call":
        _, name, args = node
        arities = {
            "vertices": 1, "edges": 1, "degree": 2, "min_degree": 1,
            "max_degree": 1, "connected": 1, "tree": 1, "bipartite": 1,
            "hamiltonian": 1, "has_perfect_matching": 1,
            "has_odd_cycle": 1,
        }
        if name not in arities:
            raise ForgeLangSemanticError(f"Unknown ForgeLang function '{name}'.")
        if len(args) != arities[name]:
            raise ForgeLangSemanticError(
                f"Function '{name}' expects {arities[name]} argument(s), got {len(args)}."
            )
        for arg in args:
            _validate_expression(arg, bound_variables, graph_variable)
        return
    if kind in {"not", "neg"}:
        _validate_expression(node[1], bound_variables, graph_variable)
        return
    if kind in {"and", "or", "implies", "iff", "+", "-", "*", "/"}:
        _validate_expression(node[1], bound_variables, graph_variable)
        _validate_expression(node[2], bound_variables, graph_variable)
        return
    if kind == "compare":
        _validate_expression(node[2], bound_variables, graph_variable)
        _validate_expression(node[3], bound_variables, graph_variable)
        return
    raise ForgeLangSemanticError(f"Unsupported expression node '{kind}'.")


def _is_bipartite(graph: Graph) -> bool:
    adjacency = graph.adjacency()
    colors: dict[int, int] = {}
    for start in range(graph.n):
        if start in colors:
            continue
        colors[start] = 0
        stack = [start]
        while stack:
            u = stack.pop()
            for v in adjacency[u]:
                if v not in colors:
                    colors[v] = 1 - colors[u]
                    stack.append(v)
                elif colors[v] == colors[u]:
                    return False
    return True


def _evaluate(node: tuple, graph: Graph, environment: dict[str, Any]) -> Any:
    kind = node[0]
    if kind == "int":
        return node[1]
    if kind == "var":
        return environment[node[1]]
    if kind == "quant":
        _, quantifier, variable, domain, body = node
        if domain[1] != "Vertices":
            raise ForgeLangSemanticError("Unsupported quantifier domain.")
        graph_name = domain[2]
        target_graph = environment.get(graph_name, graph)
        values = range(target_graph.n)
        results = []
        for value in values:
            nested = dict(environment)
            nested[variable] = value
            results.append(bool(_evaluate(body, target_graph, nested)))
        return all(results) if quantifier == "V" else any(results)
    if kind == "call":
        _, name, arguments = node
        args = [_evaluate(arg, graph, environment) for arg in arguments]
        if name == "vertices":
            return args[0].n
        if name == "edges":
            return len(args[0].edges)
        if name == "degree":
            g, vertex = args
            if not isinstance(vertex, int) or not 0 <= vertex < g.n:
                raise ForgeLangSemanticError("degree(G, v) requires v to be a vertex of G.")
            return g.degrees()[vertex]
        if name == "min_degree":
            return min(args[0].degrees(), default=0)
        if name == "max_degree":
            return max(args[0].degrees(), default=0)
        if name == "connected":
            return args[0].is_connected()
        if name == "tree":
            g = args[0]
            return g.n >= 1 and g.is_connected() and len(g.edges) == g.n - 1
        if name == "bipartite":
            return _is_bipartite(args[0])
        if name == "hamiltonian":
            return args[0].has_hamiltonian_cycle()
        if name == "has_perfect_matching":
            return args[0].has_perfect_matching()
        if name == "has_odd_cycle":
            return not _is_bipartite(args[0])
    if kind == "not":
        return not bool(_evaluate(node[1], graph, environment))
    if kind == "neg":
        value = _evaluate(node[1], graph, environment)
        if not isinstance(value, int):
            raise ForgeLangSemanticError("Unary '-' requires an integer.")
        return -value
    if kind in {"and", "or", "implies", "iff"}:
        left = bool(_evaluate(node[1], graph, environment))
        if kind == "and":
            return left and bool(_evaluate(node[2], graph, environment))
        if kind == "or":
            return left or bool(_evaluate(node[2], graph, environment))
        right = bool(_evaluate(node[2], graph, environment))
        if kind == "implies":
            return (not left) or right
        return left == right
    if kind in {"+", "-", "*", "/"}:
        left = _evaluate(node[1], graph, environment)
        right = _evaluate(node[2], graph, environment)
        if not isinstance(left, int) or not isinstance(right, int):
            raise ForgeLangSemanticError("Arithmetic operators require integer operands.")
        if kind == "+":
            return left + right
        if kind == "-":
            return left - right
        if kind == "*":
            return left * right
        if right == 0:
            raise ForgeLangSemanticError("Division by zero.")
        if left % right:
            raise ForgeLangSemanticError("ForgeLang division currently requires an integer result.")
        return left // right
    if kind == "compare":
        operator = node[1]
        left = _evaluate(node[2], graph, environment)
        right = _evaluate(node[3], graph, environment)
        try:
            return {
                "==": lambda: left == right,
                "!=": lambda: left != right,
                ">": lambda: left > right,
                "<": lambda: left < right,
                ">=": lambda: left >= right,
                "<=": lambda: left <= right,
            }[operator]()
        except TypeError:
            raise ForgeLangSemanticError(
                f"Cannot compare values of these types using '{operator}'."
            ) from None
    raise ForgeLangSemanticError(f"Unsupported expression node '{kind}'.")


def to_conjecture(parsed: ParsedConjecture) -> Conjecture:
    """Adapt a parsed universal graph claim to the existing counterexample engine."""
    _, _, graph_variable, _, body = parsed.expression

    def conclusion(graph: Graph) -> bool:
        return bool(_evaluate(body, graph, {graph_variable: graph}))

    return Conjecture(
        name=_safe_name(parsed.name),
        statement=parsed.statement,
        premise=lambda graph: True,
        conclusion=conclusion,
    )


def _safe_name(name: str) -> str:
    import re
    value = re.sub(r"[^A-Za-z0-9_-]+", "-", name.strip()).strip("-").lower()
    return value or "unnamed-conjecture"


def load_forgelang(path: str | Path) -> ParsedConjecture:
    """Read and parse a UTF-8 ForgeLang source file."""
    try:
        source = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise ForgeLangError(f"Cannot read ForgeLang file '{path}': {exc}") from exc
    return parse_forgelang(source)
