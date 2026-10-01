"""Scientific regression: feasibility-study ML projection (paper Section 5)."""

import json
from pathlib import Path

import pytest

from carbonseco_livestock.config import get_project_paths, load_scientific_params
from carbonseco_livestock.ml import predict_emissions


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "artifact_hashes.json"


def test_paper_projection_598_48() -> None:
    params = load_scientific_params()
    hashes = json.loads(FIXTURES.read_text(encoding="utf-8"))
    expected = float(hashes["paper_projection_expected_tco2e"])

    prediction = predict_emissions(
        params.paper_projection_days,
        params.paper_projection_average_dmi,
        params.paper_projection_energy_density,
        params.paper_projection_heads,
    )

    assert prediction == pytest.approx(expected, rel=1e-9, abs=1e-6)
    assert round(prediction, 2) == params.paper_projection_expected_tco2e


def test_committed_model_hash_unchanged() -> None:
    import hashlib

    paths = get_project_paths()
    hashes = json.loads(FIXTURES.read_text(encoding="utf-8"))
    digest = hashlib.sha256(paths.linear_model.read_bytes()).hexdigest()
    assert digest == hashes["models/linear_regression_model.pkl"]
