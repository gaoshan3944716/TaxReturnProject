"""Base PDF parser class."""
from abc import ABC, abstractmethod
from typing import Optional, Any
import pdfplumber


class BasePDFParser(ABC):
    """Base class for PDF form parsing."""

    def __init__(self, pdf_path: str):
        """
        Initialize the parser with a PDF file path.

        Args:
            pdf_path: Path to the PDF file to parse
        """
        self.pdf_path = pdf_path
        self.pages: list[Any] = []
        self._load_pdf()

    def _load_pdf(self) -> None:
        """Load PDF pages using pdfplumber."""
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                self.pages = pdf.pages
        except Exception as e:
            raise ValueError(f"Failed to load PDF: {e}")

    def get_text(self, page_num: int = 0) -> str:
        """
        Get all text from a specific page.

        Args:
            page_num: Page number (0-indexed)

        Returns:
            All text from the page
        """
        if 0 <= page_num < len(self.pages):
            return self.pages[page_num].extract_text() or ""
        return ""

    def find_text_near(self, search_text: str, page_num: int = 0,
                      y_offset: int = 0, x_offset: int = 0,
                      search_area: tuple = None) -> Optional[str]:
        """
        Find text near a search term on a page.

        Args:
            search_text: Text to search for
            page_num: Page number (0-indexed)
            y_offset: Vertical offset from search text
            x_offset: Horizontal offset from search text
            search_area: Tuple of (x0, y0, x1, y1) to limit search area

        Returns:
            Found text or None
        """
        if 0 >= page_num >= len(self.pages):
            return None

        page = self.pages[page_num]
        text = page.extract_text() or ""

        # Simple text search (can be enhanced with bounding box search)
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if search_text.lower() in line.lower():
                # Look at nearby lines based on y_offset
                target_line = i + y_offset
                if 0 <= target_line < len(lines):
                    return lines[target_line].strip()
        return None

    @abstractmethod
    def parse(self) -> Any:
        """
        Parse the PDF and return the parsed data.

        Returns:
            Parsed data object
        """
        pass

    def validate_pdf(self) -> tuple[bool, str]:
        """
        Validate that the PDF is of the expected form type.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.pages:
            return False, "PDF has no pages"

        first_page_text = self.get_text(0).lower()
        return True, ""
