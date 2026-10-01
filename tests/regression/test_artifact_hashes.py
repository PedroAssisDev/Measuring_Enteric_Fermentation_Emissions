"""Regression guards for committed scientific artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from carbonseco_livestock.config import get_project_paths

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "artifact_hashes.json"


@pytest.mark.parametrize(
    "relative_path",
    [
        "data/raw/pesoXleite.csv",
        "data/processed/pesoXleite_parsed.csv",
        "data/processed/sintetico.csv",
        "ontology_assets/ontologia.owl",
        "ontology_assets/ontologia_final_populada.owl",
        "ontology_assets/ontologia_populada_sync_reasoner_pellet.owl",
    ],
)
def test_artifact_sha256(relative_path: str) -> None:
    paths = get_project_paths()
    expected = json.loads(FIXTURES.read_text(encoding="utf-8"))[relative_path]
    target = paths.root / relative_path
    assert target.exists(), f"Missing artifact: {target}"
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    assert digest == expected
