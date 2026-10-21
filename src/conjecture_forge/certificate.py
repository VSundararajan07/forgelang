import json
from pathlib import Path
from .graph import Graph

FORMAT = "conjecture-forge-certificate-v1"

def write_certificate(graph, conjecture, path):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    data = {"format": FORMAT,
            "conjecture": {"name": conjecture.name, "statement": conjecture.statement},
            "graph": graph.to_dict(),
            "checks": {"premise": bool(conjecture.premise(graph)),
                       "conclusion": bool(conjecture.conclusion(graph)),
                       "is_counterexample": conjecture.is_counterexample(graph)}}
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

def verify_certificate(path, conjecture):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if data.get("format") != FORMAT: return False, "Unsupported certificate format."
        if data.get("conjecture", {}).get("name") != conjecture.name:
            return False, "Certificate conjecture name does not match."
        graph = Graph.from_dict(data["graph"])
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return False, f"Invalid certificate: {exc}"
    if not conjecture.is_counterexample(graph):
        return False, "Graph does not satisfy the counterexample condition."
    return True, "Verified: premise is true and conclusion is false for this graph."
