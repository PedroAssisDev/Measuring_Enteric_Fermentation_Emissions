"""Compatibility shim — prefer carbonseco_livestock.ontology."""

from __future__ import annotations

from carbonseco_livestock.ontology import (
    create_rules,
    generate_ontology,
    get_ontology_reasoned,
    populate_ontology,
)

# Historical aliases
generateOntology = generate_ontology
createRules = create_rules
populaOntologia = populate_ontology
getOntologia = get_ontology_reasoned

__all__ = [
    "generateOntology",
    "createRules",
    "populaOntologia",
    "getOntologia",
    "generate_ontology",
    "create_rules",
    "populate_ontology",
    "get_ontology_reasoned",
]
