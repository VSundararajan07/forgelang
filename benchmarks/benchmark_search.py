from conjecture_forge.conjectures import hamiltonicity_conjecture
from conjecture_forge.search import search_conjecture

if __name__ == "__main__":
    for bound in (4, 5):
        r = search_conjecture(hamiltonicity_conjecture(), max_vertices=bound)
        print({"max_vertices": bound, "graphs_examined": r.graphs_examined,
               "found": r.found, "elapsed_seconds": round(r.elapsed_seconds, 6)})
