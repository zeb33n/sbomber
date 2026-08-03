from sbomber.parser import Document

def todot(document: Document) -> str:
    out = "digraph {\n"
    for e in document.elements.values():
        out += f'    "{e.id}";\n'

    for r in document.relationships:
        out += f'    "{r.from_id}" -> "{r.to_id}";\n'
    
    return out + "}\n"
