
import argparse
from pathlib import Path

from .conjectures import built_in_conjectures
from .certificate import write_certificate
from .search import search_counterexample


def main():
    parser = argparse.ArgumentParser(
        description="Search graph conjectures for counterexamples."
    )
    subparsers = parser.add_subparsers(
        dest="command", required=True
    )

    subparsers.add_parser("list", help="List conjectures")

    search_parser = subparsers.add_parser(
        "search", help="Search for a counterexample"
    )
    search_parser.add_argument("conjecture")
    search_parser.add_argument(
        "--max-vertices", type=int, default=5
    )
    search_parser.add_argument(
        "--no-minimize", action="store_true"
    )
    search_parser.add_argument(
        "--no-plot",
        action="store_true",
        help="Do not open the Matplotlib window",
    )

    args = parser.parse_args()
    conjectures = built_in_conjectures()

    if args.command == "list":
        for name, conjecture in conjectures.items():
            print(name)
            print(f"  {conjecture.statement}")
        return

    if args.conjecture not in conjectures:
        parser.error(f"Unknown conjecture: {args.conjecture}")

    conjecture = conjectures[args.conjecture]
    result = search_counterexample(
        conjecture,
        max_vertices=args.max_vertices,
        minimize=not args.no_minimize,
    )

    print(f"Claim: {conjecture.statement}")
    print(
        "Graphs in requested range (upper bound): "
        f"{result.total_graphs:,}"
    )
    print(
        f"Examined {result.examined} graphs "
        f"in {result.elapsed:.4f}s"
    )

    if result.graph is None:
        print("No counterexample found in the searched range.")
        return

    graph = result.graph
    print("COUNTEREXAMPLE FOUND")
    print(f"Vertices: {graph.n}; edges: {sorted(graph.edges)}")
    print(f"Degrees: {tuple(graph.degrees())}")
    print(
        f"Premise={bool(conjecture.premise(graph))}; "
        f"conclusion={bool(conjecture.conclusion(graph))}"
    )

    output = Path("output")
    output.mkdir(parents=True, exist_ok=True)

    write_certificate(
    graph, conjecture, output / "counterexample.json"
    )
    print("Certificate written to output/counterexample.json")

    if not args.no_plot:
        from .visualize import visualize_graph

        visualize_graph(
            graph,
            title=f"Counterexample: {conjecture.name}",
            output_path=output / "counterexample.png",
        )


if __name__ == "__main__":
    main()
