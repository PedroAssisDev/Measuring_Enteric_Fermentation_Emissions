"""Compatibility shim — prefer carbonseco_livestock.preprocessing."""

from __future__ import annotations

from carbonseco_livestock.preprocessing import parse_date, parse_farm_file, parse_to_float

# Historical aliases
parse_file = parse_farm_file

__all__ = ["parse_file", "parse_farm_file", "parse_date", "parse_to_float"]


if __name__ == "__main__":
    parse_farm_file()
