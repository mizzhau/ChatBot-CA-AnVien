import sys
from pathlib import Path
from typing import Tuple

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def classify_pdf(pdf_path: Path) -> str:
    """
    Phân loại PDF: 'text_pdf', 'mixed_pdf', hoặc 'scanned_pdf'.

    Dựa trên tỷ lệ trang có text trích xuất được (>50 ký tự / trang).
    """
    import fitz  # pymupdf

    doc = fitz.open(str(pdf_path))
    total_pages = len(doc)
    if total_pages == 0:
        doc.close()
        return "scanned_pdf"

    text_pages = 0
    for page in doc:
        text = page.get_text("text").strip()
        if len(text) > 50:
            text_pages += 1

    doc.close()
    ratio = text_pages / total_pages

    if ratio > 0.8:
        return "text_pdf"
    elif ratio > 0.3:
        return "mixed_pdf"
    else:
        return "scanned_pdf"


def extract_text_pdf(pdf_path: Path) -> str:
    """Trích xuất text từ PDF text-based bằng PyMuPDF."""
    import fitz

    doc = fitz.open(str(pdf_path))
    pages = []
    for page_num, page in enumerate(doc):
        text = page.get_text("text").strip()
        if text:
            pages.append(text)
    doc.close()
    return "\n\n".join(pages)


def ocr_page_image(page, dpi: int = 300) -> str:
    """
    OCR một trang PDF bằng pytesseract.

    Trả về text từ OCR, hoặc chuỗi rỗng nếu không cài pytesseract.
    """
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        print("  [WARN] pytesseract hoặc Pillow chưa cài. Bỏ qua OCR trang này.")
        return ""

    # Render trang thành ảnh
    pix = page.get_pixmap(dpi=dpi)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    # OCR với tiếng Việt
    try:
        text = pytesseract.image_to_string(img, lang="vie")
    except Exception:
        # Fallback nếu không có lang pack tiếng Việt
        try:
            text = pytesseract.image_to_string(img, lang="eng")
            print("  [WARN] Không có lang pack 'vie'. Dùng 'eng' fallback.")
        except Exception as e:
            print(f"  [ERROR] OCR thất bại: {e}")
            text = ""
    return text.strip()


def ocr_pdf(pdf_path: Path, dpi: int = 300) -> str:
    """
    OCR toàn bộ PDF scan.

    Mỗi trang được render thành ảnh → OCR → nối lại.
    """
    import fitz

    doc = fitz.open(str(pdf_path))
    pages_text = []

    for page_num, page in enumerate(doc):
        # Thử trích text trước
        text = page.get_text("text").strip()
        if len(text) > 50:
            pages_text.append(text)
        else:
            # Trang scan → OCR
            ocr_text = ocr_page_image(page, dpi=dpi)
            if ocr_text:
                pages_text.append(f"[OCR trang {page_num + 1}]\n{ocr_text}")

    doc.close()
    return "\n\n".join(pages_text)


def pdf_to_text(pdf_path: Path) -> Tuple[str, str]:
    """
    Chuyển PDF → text, tự động chọn phương pháp.

    Returns:
        (text, quality) — quality: 'text', 'mixed', hoặc 'ocr'.
    """
    pdf_type = classify_pdf(pdf_path)

    if pdf_type == "text_pdf":
        text = extract_text_pdf(pdf_path)
        return text, "text"
    elif pdf_type == "mixed_pdf":
        text = ocr_pdf(pdf_path)
        return text, "mixed"
    else:
        text = ocr_pdf(pdf_path)
        return text, "ocr"
