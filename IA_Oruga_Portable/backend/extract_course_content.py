"""
extract_course_content.py
=========================
Extrae el texto de todos los archivos del curso (.pdf, .docx, .pptx, .ipynb)
y los convierte a archivos Markdown legibles en la carpeta `knowledge/`.

Uso:
    python scripts/extract_course_content.py
    python scripts/extract_course_content.py --source "Semestre 1 mención" --output knowledge

Dependencias:
    pip install pdfplumber python-docx python-pptx nbformat
"""

import argparse
import json
import logging
import re
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Verificación de dependencias
# ---------------------------------------------------------------------------

def _require(package: str, import_name: str | None = None):
    """Importa un paquete e informa si falta."""
    name = import_name or package
    try:
        return __import__(name)
    except ImportError:
        log.error(
            "Falta la dependencia '%s'. Instálala con:  pip install %s",
            package, package,
        )
        sys.exit(1)


# ---------------------------------------------------------------------------
# Extractores por tipo de archivo
# ---------------------------------------------------------------------------

def extract_pdf(path: Path) -> str:
    pdfplumber = _require("pdfplumber")
    lines: list[str] = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            if text.strip():
                lines.append(f"### Página {i}\n\n{text.strip()}")
    return "\n\n".join(lines) if lines else "(Sin texto extraíble)"


def extract_docx(path: Path) -> str:
    docx = _require("python-docx", "docx")
    Document = docx.Document  # type: ignore[attr-defined]
    doc = Document(str(path))
    sections: list[str] = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        style = para.style.name if para.style else ""
        if style.startswith("Heading 1"):
            sections.append(f"# {text}")
        elif style.startswith("Heading 2"):
            sections.append(f"## {text}")
        elif style.startswith("Heading 3"):
            sections.append(f"### {text}")
        else:
            sections.append(text)
    return "\n\n".join(sections) if sections else "(Sin texto extraíble)"


def extract_pptx(path: Path) -> str:
    pptx = _require("python-pptx", "pptx")
    Presentation = pptx.Presentation  # type: ignore[attr-defined]
    prs = Presentation(str(path))
    slides: list[str] = []
    for i, slide in enumerate(prs.slides, 1):
        texts: list[str] = []
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            for para in shape.text_frame.paragraphs:
                line = " ".join(run.text for run in para.runs).strip()
                if line:
                    texts.append(line)
        if texts:
            slides.append(f"### Diapositiva {i}\n\n" + "\n".join(texts))
    return "\n\n".join(slides) if slides else "(Sin texto extraíble)"


def extract_ipynb(path: Path) -> str:
    """Extrae celdas de código y markdown de un notebook Jupyter."""
    with open(path, encoding="utf-8") as f:
        nb = json.load(f)

    cells: list[str] = []
    for i, cell in enumerate(nb.get("cells", []), 1):
        ctype = cell.get("cell_type", "")
        source = "".join(cell.get("source", []))
        if not source.strip():
            continue
        if ctype == "markdown":
            cells.append(f"<!-- Celda {i}: Markdown -->\n{source}")
        elif ctype == "code":
            cells.append(f"<!-- Celda {i}: Código -->\n```python\n{source}\n```")
    return "\n\n".join(cells) if cells else "(Notebook vacío)"


def extract_csv(path: Path) -> str:
    """Genera una vista previa del CSV (primeras 50 filas)."""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        preview = lines[:51]  # encabezado + 50 filas
        note = "" if len(lines) <= 51 else f"\n\n_(Archivo truncado: {len(lines)-1} filas en total)_"
        return "```csv\n" + "".join(preview) + "```" + note
    except Exception as e:
        return f"(Error al leer CSV: {e})"


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

EXTRACTORS = {
    ".pdf":   extract_pdf,
    ".docx":  extract_docx,
    ".pptx":  extract_pptx,
    ".ipynb": extract_ipynb,
    ".csv":   extract_csv,
}


def extract_file(path: Path) -> str | None:
    """Devuelve el texto extraído o None si el tipo no está soportado."""
    extractor = EXTRACTORS.get(path.suffix.lower())
    if extractor is None:
        return None
    try:
        return extractor(path)
    except Exception as e:
        log.warning("Error al extraer '%s': %s", path.name, e)
        return f"(Error al procesar: {e})"


# ---------------------------------------------------------------------------
# Utilidades de nombres
# ---------------------------------------------------------------------------

def slugify(name: str) -> str:
    """Convierte un nombre de archivo/carpeta a slug seguro para el sistema."""
    name = name.strip()
    # elimina extensión
    stem = Path(name).stem
    # reemplaza caracteres problemáticos
    slug = re.sub(r"[^\w\s\-]", "", stem, flags=re.UNICODE)
    slug = re.sub(r"[\s]+", "_", slug)
    return slug[:120]  # límite de longitud


# ---------------------------------------------------------------------------
# Procesador principal
# ---------------------------------------------------------------------------

def build_header(source_path: Path, relative_to: Path) -> str:
    """Genera un encabezado Markdown con metadatos del archivo fuente."""
    rel = source_path.relative_to(relative_to)
    size_kb = source_path.stat().st_size / 1024
    return (
        f"# {source_path.stem}\n\n"
        f"> **Fuente:** `{rel}`  \n"
        f"> **Tipo:** `{source_path.suffix.upper()}`  \n"
        f"> **Tamaño:** `{size_kb:.1f} KB`\n\n"
        "---\n\n"
    )


def process_directory(source_root: Path, output_root: Path) -> dict:
    """
    Recorre source_root recursivamente, extrae texto de los archivos
    soportados y guarda archivos .md en output_root.

    Retorna un dict con estadísticas: total, ok, errores, omitidos.
    """
    stats = {"total": 0, "ok": 0, "error": 0, "skipped": 0}

    supported_extensions = set(EXTRACTORS.keys())

    for source_path in sorted(source_root.rglob("*")):
        if not source_path.is_file():
            continue
        if source_path.suffix.lower() not in supported_extensions:
            stats["skipped"] += 1
            continue

        stats["total"] += 1

        # Calcular ruta de destino
        try:
            rel_parts = source_path.relative_to(source_root).parts
        except ValueError:
            rel_parts = (source_path.name,)

        # Construir carpeta destino con la misma jerarquía
        dest_dir = output_root.joinpath(*rel_parts[:-1])
        dest_dir.mkdir(parents=True, exist_ok=True)

        dest_file = dest_dir / (slugify(source_path.stem) + ".md")

        # Extraer contenido
        content = extract_file(source_path)
        if content is None:
            stats["skipped"] += 1
            continue

        header = build_header(source_path, source_root.parent)
        full_content = header + content

        try:
            dest_file.write_text(full_content, encoding="utf-8")
            log.info("✅ %s → %s", source_path.name, dest_file.relative_to(output_root))
            stats["ok"] += 1
        except Exception as e:
            log.warning("❌ No se pudo escribir '%s': %s", dest_file, e)
            stats["error"] += 1

    return stats


def generate_index(output_root: Path) -> None:
    """Genera un archivo INDEX.md con la lista de todo el conocimiento extraído."""
    index_lines = [
        "# 📚 Índice del Conocimiento Extraído\n",
        "_Generado automáticamente por `extract_course_content.py`_\n\n",
    ]

    current_section = None
    for md_file in sorted(output_root.rglob("*.md")):
        if md_file.name == "INDEX.md":
            continue
        try:
            rel = md_file.relative_to(output_root)
        except ValueError:
            continue

        # Sección por primera carpeta
        section = rel.parts[0] if len(rel.parts) > 1 else "General"
        if section != current_section:
            index_lines.append(f"\n## {section}\n")
            current_section = section

        indent = "  " * (len(rel.parts) - 2) if len(rel.parts) > 2 else ""
        index_lines.append(f"{indent}- [{rel.stem}]({rel})")

    index_path = output_root / "INDEX.md"
    index_path.write_text("\n".join(index_lines), encoding="utf-8")
    log.info("📋 Índice generado en %s", index_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extrae contenido de archivos del curso a Markdown."
    )
    parser.add_argument(
        "--source",
        default="Semestre 1 mención",
        help="Carpeta raíz con el material del curso (relativa al repo).",
    )
    parser.add_argument(
        "--output",
        default="knowledge",
        help="Carpeta destino para los archivos Markdown extraídos.",
    )
    parser.add_argument(
        "--no-index",
        action="store_true",
        help="Omitir la generación del índice INDEX.md.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Resolver rutas relativas al directorio del repo (padre de scripts/)
    repo_root = Path(__file__).resolve().parent.parent
    source_root = (repo_root / args.source).resolve()
    output_root = (repo_root / args.output).resolve()

    if not source_root.exists():
        log.error("La carpeta fuente no existe: %s", source_root)
        sys.exit(1)

    output_root.mkdir(parents=True, exist_ok=True)

    log.info("🔍 Leyendo: %s", source_root)
    log.info("📁 Destino: %s", output_root)
    log.info("")

    stats = process_directory(source_root, output_root)

    if not args.no_index:
        generate_index(output_root)

    log.info("")
    log.info("=" * 50)
    log.info("Archivos procesados : %d", stats["total"])
    log.info("Exitosos            : %d", stats["ok"])
    log.info("Errores             : %d", stats["error"])
    log.info("Omitidos            : %d", stats["skipped"])
    log.info("=" * 50)


if __name__ == "__main__":
    main()
