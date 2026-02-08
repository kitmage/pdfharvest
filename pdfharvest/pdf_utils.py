"""PDF reading and OCR utilities."""

from pathlib import Path

from pdf2image import convert_from_path
import pytesseract
from pypdf import PdfReader

from pdfharvest.config import DEFAULT_OCR_DPI
from pdfharvest.exceptions import PDFError


def get_total_pages(pdf_path: Path) -> int:
    """
    Return the number of pages in the PDF.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Page count (>= 0).

    Raises:
        PDFError: If the file cannot be read as a PDF.
    """
    try:
        reader = PdfReader(str(pdf_path))
        return len(reader.pages)
    except Exception as e:
        raise PDFError(f"Failed to read PDF: {e}") from e


def extract_text_from_page(reader: PdfReader, page_index: int) -> str:
    """
    Extract text from a single page using pypdf (no OCR).

    Args:
        reader: Open PdfReader instance.
        page_index: Zero-based page index.

    Returns:
        Extracted text, or empty string if none.
    """
    page = reader.pages[page_index]
    return (page.extract_text() or "").strip()


def ocr_page(
    pdf_path: Path,
    page_number: int,
    temp_dir: str,
    dpi: int = DEFAULT_OCR_DPI,
) -> str:
    """
    Run Tesseract OCR on a single PDF page when native text is missing.

    Args:
        pdf_path: Path to the PDF file.
        page_number: One-based page number (as in pypdf enumeration).
        temp_dir: Directory for temporary rendered images.
        dpi: Resolution for rendering.

    Returns:
        OCR text for the page, or empty string if OCR fails or yields nothing.
    """
    try:
        images = convert_from_path(
            str(pdf_path),
            first_page=page_number,
            last_page=page_number,
            dpi=dpi,
            fmt="png",
            output_folder=temp_dir,
        )
    except Exception:
        return ""
    if not images:
        return ""
    image = images[0]
    try:
        return pytesseract.image_to_string(image) or ""
    finally:
        try:
            image.close()
        except Exception:
            pass
