from pathlib import Path
import shutil
from sbomber.parser import Document


def generate_output(document: Document, output_path: Path):
    if output_path.is_dir():
        shutil.rmtree(output_path)
    output_path.mkdir(parents=True, exist_ok=False)

    (output_path / "sbom.dot").write_text(document_to_dot(document))
    (output_path / "sbom.md").write_text(document_to_md(document, output_path))
    (output_path / "index.md").write_text("# SBOMBER\n[Explore your SBOM](sbom.md)\n")
    (output_path / "sbom.css").write_text(create_style_sheet())


def get_label(document: Document, id: str) -> str:
    return document.elements[id].info.get("name", id)


def document_to_md(document: Document, output_path: Path) -> str:
    out = f"""---
hide:
  - navigation
  - toc
---

# SBOM

<div class="sbomber-container" markdown>

{{{{ dag_viewer("90vw", "600px", "{output_path / 'sbom.dot'}") }}}}

<div class="sbomber-info" markdown>
"""

    for e in document.elements.values():
        info = "| key | value |\n| - | - |\n"
        info += "\n".join([f"| {k} | {v} |" for k, v in e.info.items()])

        e_label = get_label(document, e.id)
        
        parents = "### Parents\n\n" if e.in_edge_handles else ""
        for h in e.in_edge_handles:
            relationship = document.relationships[h]
            from_label = get_label(document, relationship.from_id)
            anchor = from_label.replace(".", "").lower()
            parents += f"- [{from_label}](sbom.md#{anchor}) {relationship.kind} {e_label}\n"

        children = "### Children\n\n" if e.out_edge_handles else ""
        for h in e.out_edge_handles:
            relationship = document.relationships[h]
            to_label = get_label(document, relationship.to_id)
            anchor = to_label.replace(".", "").lower()
            children += f"- {e_label} {relationship.kind} [{to_label}](sbom.md#{anchor})\n"

        out += f"""
## {e_label.title()}

### Info

{info}

{parents}
{children}
"""
    return out + "\n</div>\n</div>"


def document_to_dot(document: Document) -> str:
    out = "digraph {\n"
    for e in document.elements.values():
        label = get_label(document, e.id)
        anchor = label.replace(".", "").lower()
        out += f'    "{e.id}" [dv_label="{label}", dv_link="sbom.html#{anchor}"];\n'

    for r in document.relationships:
        out += f'    "{r.from_id}" -> "{r.to_id}";\n'

    return out + "}\n"

def create_style_sheet() -> str:
    return """
.md-grid {
  max-width: none; 
}

.sbomber-info {
  width: 30vw;
  height: 600px;
  overflow-y: auto;
  min-height: 0;
}

.sbomber-container {
  display:flex;
  align-items:flex-start;
  gap:16px;   
}
"""
    
