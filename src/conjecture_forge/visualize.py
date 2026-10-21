
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx


def visualize_graph(
    graph,
    title="Counterexample",
    output_path="output/counterexample.png",
):
    # Convert the project's graph into a NetworkX graph.
    G = nx.Graph()
    G.add_nodes_from(range(graph.n))
    G.add_edges_from(graph.edges)

    # Label each vertex with its ID and degree.
    degrees = dict(G.degree())
    labels = {
        v: f"{v}\ndeg={degrees[v]}"
        for v in G.nodes()
    }

    # Compute positions for a readable layout.
    pos = nx.spring_layout(G, seed=42)

    fig, ax = plt.subplots(figsize=(8, 6))

    nx.draw_networkx_edges(
        G, pos, ax=ax, width=2, edge_color="gray"
    )
    nx.draw_networkx_nodes(
        G,
        pos,
        ax=ax,
        node_size=1400,
        node_color="lightblue",
        edgecolors="navy",
        linewidths=1.5,
    )
    nx.draw_networkx_labels(
        G, pos, labels=labels, ax=ax, font_size=10
    )

    ax.set_title(title)
    ax.axis("off")
    fig.tight_layout()

    # Save a copy of the graph.
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    print(f"Graph image saved to: {path.resolve()}")

    # Opens a Matplotlib window with zoom/pan controls.
    plt.show()
