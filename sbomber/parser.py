from pathlib import Path
from dataclasses import dataclass
import json

from sbomber.error import SbomberError, raise_error_if


@dataclass
class Element:
    id: str
    in_edge_handles: list[int]
    out_edge_handles: list[int]
    info: dict[str, str]


@dataclass
class RelationShip:
    kind: str
    from_id: str
    to_id: str


@dataclass
class Document:
    elements: dict[str, Element]
    relationships: list[RelationShip]


def parse(file: Path) -> Document:
    data = json.loads(file.read_bytes())
    element_data = data.pop("packages")
    relationship_data = data.pop("relationships")
    
    document_id = data.get("SPDXID")
    raise_error_if(document_id is None, "No Document level SPDXID")
    elements = {document_id: Element(document_id, [], [], data)}

    for e in element_data:
        id = e.get("SPDXID")
        raise_error_if(id is None, "Package missing SPDXID key")
        elements[id] = Element(id, [], [], e)

    relationships = []
    for i, r in enumerate(relationship_data):
        to_id = r.get("spdxElementId")
        raise_error_if(to_id is None, "Relationship missing spdxElementId key")
        from_id = r.get("relatedSpdxElement")
        raise_error_if(from_id is None, "Relationship missing relatedSpdxElement key")
        kind = r.get("relationshipType", "IS RELATED TO")

        relationship = RelationShip(kind, from_id, to_id)
        relationships.append(relationship)

        from_element = elements.get(from_id)
        raise_error_if(from_element is None, f"{from_id} is not in {file}")
        from_element.out_edge_handles.append(i)

        to_element = elements.get(to_id)
        raise_error_if(to_element is None, f"{to_id} is not in {file}")
        from_element.in_edge_handles.append(i)

    return Document(elements, relationships)
