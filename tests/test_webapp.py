import pytest
from webapp import EXAMPLE, run_check


def test_empty_input_is_rejected():
    status, data = run_check({"source": "  "})
    assert status == 400
    assert data["status"] == "INVALID_FORMULA"


def test_invalid_forgelang_returns_helpful_error():
    status, data = run_check({"source": "not a conjecture"})
    assert status == 400
    assert data["status"] == "INVALID_FORMULA"
    assert "error" in data


def test_invalid_search_bounds_are_rejected():
    status, data = run_check({"source": EXAMPLE, "max_vertices": 99})
    assert status == 400
    assert data["status"] == "INVALID_SETTINGS"


def test_hamiltonian_conjecture_finds_counterexample():
    status, data = run_check({"source": EXAMPLE, "max_vertices": 5, "max_graphs": 100000})
    assert status == 200
    assert data["status"] == "COUNTEREXAMPLE_FOUND"
    assert data["graph"]["n"] == 5
    assert data["formula_value"] is False
