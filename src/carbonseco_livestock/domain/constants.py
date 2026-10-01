"""Domain-level identifiers shared across ontology and query layers."""

from __future__ import annotations

ONTOLOGY_IRI = "http://www.semanticweb.org/owl/owlapi/EntericMeasureOnto#"


class OntologyIRI:
    """Convenience namespace for EntericMeasureOnto."""

    BASE = ONTOLOGY_IRI
    RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    RDFS = "http://www.w3.org/2000/01/rdf-schema#"
    XSD = "http://www.w3.org/2001/XMLSchema#"
