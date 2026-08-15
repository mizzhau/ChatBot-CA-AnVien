import re
import sys
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


# ─────────────────────────────────────────────────────────────────────
#  DOCX → Markdown
# ─────────────────────────────────────────────────────────────────────

def docx_to_markdown(docx_path: Path) -> str:
    """Chuyển file .docx sang markdown, giữ cấu trúc heading / bảng."""
    from docx import Document
    from docx.table import Table as DocxTable
    from docx.text.paragraph import Paragraph
    from docx.oxml.ns import qn

    doc = Document(str(docx_path))
    md_parts: list[str] = []

    for child in doc.element.body.iterchildren():
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag

        if tag == "p":
            para = Paragraph(child, doc)
            line = _para_to_md(para)
            if line is not None:
                md_parts.append(line)

        elif tag == "tbl":
            table = DocxTable(child, doc)
            md_table = _table_to_md(table)
            if md_table:
                md_parts.append("")
                md_parts.append(md_table)
                md_parts.append("")

    text = "\n".join(md_parts)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _para_to_md(para) -> Optional[str]:
    """Chuyển 1 paragraph Word → dòng markdown."""
    text = para.text.strip()
    if not text:
        return ""

    style_name = (para.style.name or "").lower() if para.style else ""

    # ── Word heading styles ──
    if "heading 1" in style_name or style_name == "title":
        return f"# {text}"
    if "heading 2" in style_name:
        return f"## {text}"
    if "heading 3" in style_name:
        return f"### {text}"
    if "heading 4" in style_name:
        return f"#### {text}"
    if "list bullet" in style_name:
        return f"- {text}"
    if "list number" in style_name:
        return f"1. {text}"

    # ── Vietnamese legal document patterns ──
    # Phần
    phan_m = re.match(
        r"^(?:PHẦN|Phần)\s+([IVXLCDM\d]+)[.:\s–\-]+(.*)$", text
    )
    if phan_m:
        return f"# Phần {phan_m.group(1)}: {phan_m.group(2).strip()}"

    # Chương
    chuong_m = re.match(
        r"^(?:CHƯƠNG|Chương)\s+([IVXLCDM\d]+)[.:\s–\-]*(.*)$", text
    )
    if chuong_m:
        title = chuong_m.group(2).strip()
        sep = ": " if title else ""
        return f"## Chương {chuong_m.group(1)}{sep}{title}"

    # Mục
    muc_m = re.match(r"^(?:MỤC|Mục)\s+(\d+)[.:\s–\-]*(.*)$", text)
    if muc_m:
        return f"### Mục {muc_m.group(1)}. {muc_m.group(2).strip()}"

    # Điều
    dieu_m = re.match(
        r"^(?:Điều|ĐIỀU|Dieu)\s+(\d+[a-z]?)\.\s*(.*)$", text
    )
    if dieu_m:
        return f"### Điều {dieu_m.group(1)}. {dieu_m.group(2).strip()}"

    # ── Bold-only paragraphs ngắn → có thể là heading ──
    if _is_all_bold(para) and len(text) < 200:
        # Kiểm tra nếu toàn bộ UPPERCASE → có thể là heading lớn
        if text == text.upper() and len(text) < 100:
            return f"## {text}"
        return f"**{text}**"

    return text


def _is_all_bold(para) -> bool:
    """Kiểm tra toàn bộ runs trong paragraph có bold không."""
    runs = para.runs
    if not runs:
        return False
    text_runs = [r for r in runs if r.text.strip()]
    if not text_runs:
        return False
    return all(r.bold for r in text_runs)


def _table_to_md(table) -> str:
    """Chuyển bảng Word → bảng markdown."""
    rows: list[list[str]] = []
    for row in table.rows:
        cells = []
        for cell in row.cells:
            cell_text = cell.text.strip().replace("\n", " ").replace("|", "\\|")
            cells.append(cell_text)
        rows.append(cells)

    if not rows:
        return ""

    max_cols = max(len(r) for r in rows)
    for r in rows:
        while len(r) < max_cols:
            r.append("")

    lines = []
    lines.append("| " + " | ".join(rows[0]) + " |")
    lines.append("| " + " | ".join(["---"] * max_cols) + " |")
    for row in rows[1:]:
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────
#  DOC → Markdown (qua LibreOffice hoặc fallback)
# ─────────────────────────────────────────────────────────────────────

def doc_to_markdown(doc_path: Path) -> str:
    """
    Chuyển file .doc (Word 97-2003) → markdown.

    Thử theo thứ tự:
      1. LibreOffice headless → .docx → parse
      2. Đọc raw text với fallback
    """
    # Thử convert bằng LibreOffice
    docx_path = _convert_doc_via_libreoffice(doc_path)
    if docx_path and docx_path.exists():
        try:
            result = docx_to_markdown(docx_path)
            docx_path.unlink(missing_ok=True)  # Xóa file tạm
            return result
        except Exception:
            docx_path.unlink(missing_ok=True)

    # Fallback: đọc raw text
    return _doc_raw_text(doc_path)


def _convert_doc_via_libreoffice(doc_path: Path) -> Optional[Path]:
    """Gọi LibreOffice headless để convert .doc → .docx."""
    tmp_dir = tempfile.mkdtemp()
    for cmd in ["soffice", "libreoffice"]:
        try:
            subprocess.run(
                [
                    cmd, "--headless", "--convert-to", "docx",
                    "--outdir", tmp_dir,
                    str(doc_path),
                ],
                capture_output=True, timeout=120, check=True,
            )
            docx_name = doc_path.stem + ".docx"
            result = Path(tmp_dir) / docx_name
            if result.exists():
                return result
        except (FileNotFoundError, subprocess.SubprocessError):
            continue
    return None


def _doc_raw_text(doc_path: Path) -> str:
    """Đọc raw bytes của .doc và lọc text Unicode — fallback cuối cùng."""
    try:
        raw = doc_path.read_bytes()
        # Thử decode UTF-8 trước, rồi cp1252
        for enc in ("utf-8", "cp1252", "latin-1"):
            try:
                text = raw.decode(enc, errors="ignore")
                break
            except Exception:
                continue
        else:
            text = raw.decode("latin-1", errors="ignore")

        # Lọc chỉ giữ printable characters
        cleaned = re.sub(r"[^\x20-\x7E\u00C0-\u024F\u1E00-\u1EFF\n\r\t]", " ", text)
        cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        return cleaned.strip()
    except Exception as e:
        return f"[ERROR] Không thể đọc file .doc: {e}"


# ─────────────────────────────────────────────────────────────────────
#  PDF → Markdown
# ─────────────────────────────────────────────────────────────────────

def pdf_to_markdown(pdf_path: Path) -> tuple[str, str]:
    """
    Chuyển PDF → markdown text.

    Returns:
        (markdown_text, doc_quality) — quality: 'text' / 'mixed' / 'ocr'.
    """
    from src.ingestion.ocr_processor import pdf_to_text

    raw_text, quality = pdf_to_text(pdf_path)

    # Post-process: chuyển cấu trúc pháp luật VN thành markdown heading
    md_text = _structure_legal_text(raw_text)

    return md_text, quality


def _structure_legal_text(text: str) -> str:
    """Thêm markdown heading cho cấu trúc văn bản pháp luật VN."""
    lines = text.split("\n")
    result = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            result.append("")
            continue

        # Phần
        phan_m = re.match(
            r"^(?:PHẦN|Phần)\s+([IVXLCDM\d]+)[.:\s–\-]+(.*)$", stripped
        )
        if phan_m:
            result.append(f"# Phần {phan_m.group(1)}: {phan_m.group(2).strip()}")
            continue

        # Chương
        chuong_m = re.match(
            r"^(?:CHƯƠNG|Chương)\s+([IVXLCDM\d]+)[.:\s–\-]*(.*)$", stripped
        )
        if chuong_m:
            title = chuong_m.group(2).strip()
            sep = ": " if title else ""
            result.append(f"## Chương {chuong_m.group(1)}{sep}{title}")
            continue

        # Mục
        muc_m = re.match(r"^(?:MỤC|Mục)\s+(\d+)[.:\s–\-]*(.*)$", stripped)
        if muc_m:
            result.append(
                f"### Mục {muc_m.group(1)}. {muc_m.group(2).strip()}"
            )
            continue

        # Điều
        dieu_m = re.match(
            r"^(?:Điều|ĐIỀU|Dieu)\s+(\d+[a-z]?)\.\s*(.*)$", stripped
        )
        if dieu_m:
            result.append(
                f"### Điều {dieu_m.group(1)}. {dieu_m.group(2).strip()}"
            )
            continue

        result.append(stripped)

    text = "\n".join(result)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ─────────────────────────────────────────────────────────────────────
#  Entrypoint chung
# ─────────────────────────────────────────────────────────────────────

def convert_file(
    input_path: Path,
    output_dir: Path,
    source_id: str,
) -> Optional[Path]:
    """
    Chuyển 1 file đầu vào → <output_dir>/<source_id>.md

    Returns:
        Path đến file .md đã tạo, hoặc None nếu lỗi / bỏ qua.
    """
    suffix = input_path.suffix.lower()
    output_path = output_dir / f"{source_id}.md"

    try:
        if suffix == ".docx":
            md_text = docx_to_markdown(input_path)
        elif suffix == ".doc":
            md_text = doc_to_markdown(input_path)
        elif suffix == ".pdf":
            md_text, quality = pdf_to_markdown(input_path)
            # Thêm header ghi chú chất lượng cho file OCR
            if quality in ("ocr", "mixed"):
                header = (
                    f"<!-- doc_quality: {quality} -->\n"
                    f"<!-- Nguồn: {input_path.name} -->\n\n"
                )
                md_text = header + md_text
        elif suffix == ".pptx":
            print(f"  [SKIP] .pptx tạm loại: {input_path.name}")
            return None
        else:
            print(f"  [SKIP] Định dạng không hỗ trợ: {suffix}")
            return None

        if not md_text or len(md_text.strip()) < 20:
            print(f"  [WARN] Nội dung trích xuất quá ngắn: {input_path.name}")
            return None

        output_dir.mkdir(parents=True, exist_ok=True)
        output_path.write_text(md_text, encoding="utf-8")
        return output_path

    except Exception as e:
        print(f"  [ERROR] {input_path.name}: {e}", file=sys.stderr)
        return None
