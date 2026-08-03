from pathlib import Path
import shutil
from sbomber.parser import Document, Element


def generate_output(document: Document, output_path: Path):
    if output_path.is_dir():
        shutil.rmtree(output_path)
    output_path.mkdir(parents=True, exist_ok=False)

    (output_path / "sbom.dot").write_text(document_to_dot(document))
    (output_path / "sbom.md").write_text(document_to_md(document))
    (output_path / "index.md").write_text("#SBOMBER\n")


def document_to_md(document: Document) -> str:
    out = ""

    for e in document.elements.values():
        info = "| key | value |\n| - | - |\n"
        info += "\n".join([f"| {k} | {v} |" for k, v in e.info.items()])
        parents = "### Parents\n\n" if e.in_edge_handles else ""
        for h in e.in_edge_handles:
            relationship = document.relationships[h]
            anchor = relationship.from_id.replace(".", "").lower()
            parents += f"- [{relationship.from_id}](sbom#{anchor}) {relationship.kind} {e.id}\n"

        children = "### Children\n\n" if e.out_edge_handles else ""
        for h in e.out_edge_handles:
            relationship = document.relationships[h]
            anchor = relationship.to_id.replace(".", "").lower()
            children += f"- {e.id} {relationship.kind} [{relationship.to_id}](sbom#{anchor})\n"

        out += f"""
## {e.id}

### Info

{info}

{parents}
{children}
"""
    return out


def document_to_dot(document: Document) -> str:
    out = "digraph {\n"
    for e in document.elements.values():
        out += f'    "{e.id}";\n'

    for r in document.relationships:
        out += f'    "{r.from_id}" -> "{r.to_id}";\n'

    return out + "}\n"
