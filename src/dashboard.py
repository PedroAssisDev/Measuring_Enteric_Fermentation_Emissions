"""Compatibility shim — prefer carbonseco_livestock.visualization.dashboard."""

from __future__ import annotations

from carbonseco_livestock.visualization.dashboard import run_dashboard

if __name__ == "__main__":
    run_dashboard()
