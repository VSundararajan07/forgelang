import argparse
import json
import sys
from .certificate import verify_certificate, write_certificate
from .conjectures import built_in_conjectures
from .generator import estimate_total_graphs
from .minimize import minimize_counterexample
from .search import search_conjecture
from .forgelang import ForgeLangError, load_forgelang, to_conjecture

def main(argv=None):
    parser = argparse.ArgumentParser(description="Search small graphs for counterexamples.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    search = sub.add_parser("search")
    search.add_argument("conjecture")
    search.add_argument("--max-vertices", type=int, default=5)
    search.add_argument("--min-vertices", type=int, default=1)
    search.add_argument("--max-graphs", type=int)
    search.add_argument("--output", default="output/counterexample.json")
    search.add_argument("--no-minimize", action="store_true")
    check = sub.add_parser("check", help="Check a ForgeLang .forge conjecture")
    check.add_argument("file")
    check.add_argument("--max-vertices", type=int, default=5)
    check.add_argument("--min-vertices", type=int, default=1)
    check.add_argument("--max-graphs", type=int)
    check.add_argument("--output", default="output/counterexample.json")
    check.add_argument("--no-minimize", action="store_true")
    verify = sub.add_parser("verify")
    verify.add_argument("certificate")
    args = parser.parse_args(argv)
    conjectures = built_in_conjectures()
    if args.command == "check":
        try:
            parsed = load_forgelang(args.file)
            c = to_conjecture(parsed)
        except ForgeLangError as exc:
            print(f"ForgeLang error: {exc}", file=sys.stderr)
            return 2
        if args.max_vertices > 7:
            print("Warning: exhaustive graph enumeration grows extremely quickly.", file=sys.stderr)
        print(f"Claim: {c.statement}")
        print(f"Searching graphs with {args.min_vertices} to {args.max_vertices} vertices.")
        result = search_conjecture(c, args.max_vertices, args.min_vertices, args.max_graphs)
        print(f"Examined {result.graphs_examined:,} graphs in {result.elapsed_seconds:.4f}s")
        if not result.found:
            print("NO_COUNTEREXAMPLE_WITHIN_BOUND")
            print("No counterexample found in explored search. This is not a proof.")
            return 1
        graph = result.counterexample
        if not args.no_minimize:
            graph = minimize_counterexample(graph, c)
        print("COUNTEREXAMPLE_FOUND")
        print(f"Vertices: {graph.n}; edges: {sorted(graph.edges)}; degrees: {graph.degrees()}")
        print(f"Formula evaluates to: {bool(c.conclusion(graph))}")
        write_certificate(graph, c, args.output)
        print(f"Certificate written to {args.output}")
        return 0
    if args.command == "list":
        for name, c in conjectures.items(): print(f"{name}\n  {c.statement}\n")
        return 0
    if args.command == "verify":
        try:
            data = json.loads(open(args.certificate, encoding="utf-8").read())
            name = data["conjecture"]["name"]
            c = conjectures[name]
        except (OSError, ValueError, KeyError, TypeError) as exc:
            print(f"Could not load known conjecture certificate: {exc}", file=sys.stderr)
            return 2
        ok, message = verify_certificate(args.certificate, c)
        print(message)
        return 0 if ok else 1
    if args.conjecture not in conjectures:
        parser.error("unknown conjecture; run 'list' to see available choices")
    if args.max_vertices > 7:
        print("Warning: exhaustive graph enumeration grows extremely quickly.", file=sys.stderr)
    c = conjectures[args.conjecture]
    print(f"Claim: {c.statement}")
    print(f"Graphs in requested range (upper bound): {estimate_total_graphs(args.max_vertices, args.min_vertices):,}")
    result = search_conjecture(c, args.max_vertices, args.min_vertices, args.max_graphs)
    print(f"Examined {result.graphs_examined:,} graphs in {result.elapsed_seconds:.4f}s")
    if not result.found:
        print("No counterexample found in explored search. This is not a proof.")
        return 1
    graph = result.counterexample
    if not args.no_minimize: graph = minimize_counterexample(graph, c)
    print("COUNTEREXAMPLE FOUND")
    print(f"Vertices: {graph.n}; edges: {sorted(graph.edges)}; degrees: {graph.degrees()}")
    print(f"Premise={bool(c.premise(graph))}; conclusion={bool(c.conclusion(graph))}")
    write_certificate(graph, c, args.output)
    print(f"Certificate written to {args.output}")
    print("Minimization is greedy; global minimality is not guaranteed.")
    return 0
