"""W-2 form PDF parser."""
import re
from typing import Optional, Tuple
from .base_parser import BasePDFParser
from ..models.w2 import W2


class W2Parser(BasePDFParser):
    """Parser for W-2 Wage and Tax Statement forms."""

    # Common patterns for W-2 forms
    W2_KEYWORDS = ['w-2', 'wage and tax statement', 'form w-2']
    BOX_PATTERNS = {
        'box1': [r'wages,.*tips.*compensation', r'box\s*1', r'^1\s*[\.\s]+([0-9,]+\.?\d*)'],
        'box2': [r'federal income tax withheld', r'box\s*2', r'^2\s*[\.\s]+([0-9,]+\.?\d*)'],
        'box3': [r'social security wages', r'box\s*3', r'^3\s*[\.\s]+([0-9,]+\.?\d*)'],
        'box4': [r'social security tax', r'box\s*4', r'^4\s*[\.\s]+([0-9,]+\.?\d*)'],
        'box5': [r'medicare wages', r'box\s*5', r'^5\s*[\.\s]+([0-9,]+\.?\d*)'],
        'box6': [r'medicare tax', r'box\s*6', r'^6\s*[\.\s]+([0-9,]+\.?\d*)'],
        'box16': [r'state wages.*tips', r'box\s*16', r'^16\s*[\.\s]+([0-9,]+\.?\d*)'],
        'box17': [r'state income tax', r'box\s*17', r'^17\s*[\.\s]+([0-9,]+\.?\d*)'],
    }

    def validate_pdf(self) -> Tuple[bool, str]:
        """Validate that the PDF is a W-2 form."""
        is_valid, error = super().validate_pdf()
        if not is_valid:
            return is_valid, error

        text = self.get_text(0).lower()
        has_w2_keywords = any(keyword in text for keyword in self.W2_KEYWORDS)

        if not has_w2_keywords:
            return False, "PDF does not appear to be a W-2 form"

        return True, ""

    def parse(self) -> W2:
        """
        Parse the W-2 PDF and return a W2 object.

        Returns:
            W2 object with parsed data
        """
        w2 = W2()

        # Parse all pages
        all_text = ""
        for i in range(len(self.pages)):
            all_text += self.get_text(i) + "\n"

        # Try to extract data using multiple strategies
        w2 = self._extract_with_patterns(w2, all_text)
        w2 = self._extract_with_coordinate_search(w2)
        w2 = self._extract_employer_info(w2, all_text)
        w2 = self._extract_employee_info(w2, all_text)
        w2 = self._extract_state_info(w2, all_text)

        return w2

    def _extract_with_patterns(self, w2: W2, text: str) -> W2:
        """Extract data using regex patterns from text."""
        # Look for SSN pattern
        ssn_pattern = r'\d{3}[-\s]?\d{2}[-\s]?\d{4}'
        ssn_matches = re.findall(ssn_pattern, text)
        if ssn_matches:
            # Usually first SSN is employee's, second is employer's EIN
            w2.employee_ssn = ssn_matches[0].replace(' ', '-')
            if len(ssn_matches) > 1:
                w2.employer_ein = ssn_matches[1].replace(' ', '-')

        # Look for dollar amounts in various formats
        amount_pattern = r'\$?\s*([0-9,]+\.?\d*)\s*\$?'
        amounts = re.findall(amount_pattern, text)

        return w2

    def _extract_with_coordinate_search(self, w2: W2) -> W2:
        """Extract data using coordinate-based search."""
        if not self.pages:
            return w2

        # Try to find numeric values near box labels
        # This is a simplified approach - real implementation would need
        # coordinate mapping for different W-2 form formats
        page = self.pages[0]
        words = page.extract_words()

        # Group words by their y-coordinate (line)
        lines = {}
        for word in words:
            y = int(word['top'] / 10) * 10  # Group by 10-pixel lines
            if y not in lines:
                lines[y] = []
            lines[y].append(word)

        # Look for numbers that could be wages/taxes
        for y in sorted(lines.keys()):
            line_words = lines[y]
            for word in line_words:
                if re.match(r'^[0-9,]+\.\d{2}$', word['text']):
                    # This looks like a monetary value
                    # Position on page helps identify which box it belongs to
                    value = float(word['text'].replace(',', ''))
                    x = word['x0']

                    # Rough coordinate mapping (varies by form)
                    if 200 < x < 300:  # Left side - Box 1 area
                        w2.box1_wages = max(w2.box1_wages, value)
                    elif 400 < x < 500:  # Box 2 area
                        w2.box2_federal_tax = max(w2.box2_federal_tax, value)

        return w2

    def _extract_employer_info(self, w2: W2, text: str) -> W2:
        """Extract employer information."""
        lines = text.split('\n')

        # Look for employer name (usually near top, after "Employer's name")
        for i, line in enumerate(lines):
            if 'employer' in line.lower() and 'name' in line.lower():
                # Next few lines likely contain employer info
                if i + 1 < len(lines) and lines[i + 1].strip():
                    w2.employer_name = lines[i + 1].strip()

        return w2

    def _extract_employee_info(self, w2: W2, text: str) -> W2:
        """Extract employee information."""
        lines = text.split('\n')

        # Look for employee name
        for i, line in enumerate(lines):
            if 'employee' in line.lower() and 'name' in line.lower():
                # Next line likely has employee name
                if i + 1 < len(lines) and lines[i + 1].strip():
                    parts = lines[i + 1].strip().split()
                    if parts:
                        # Assume format: Lastname Firstname or Firstname Lastname
                        if len(parts) >= 2:
                            w2.employee_name = lines[i + 1].strip()

        return w2

    def _extract_state_info(self, w2: W2, text: str) -> W2:
        """Extract state-related information."""
        # Look for state abbreviation
        state_pattern = r'\b(CA|California)\b'
        if re.search(state_pattern, text, re.IGNORECASE):
            w2.state_code = 'CA'

        return w2


def parse_w2_pdf(pdf_path: str) -> Optional[W2]:
    """
    Parse a W-2 PDF file and return a W2 object.

    Args:
        pdf_path: Path to the W-2 PDF file

    Returns:
        W2 object with parsed data, or None if parsing fails
    """
    try:
        parser = W2Parser(pdf_path)
        is_valid, error = parser.validate_pdf()
        if not is_valid:
            print(f"Invalid W-2 PDF: {error}")
            return None
        return parser.parse()
    except Exception as e:
        print(f"Error parsing W-2 PDF: {e}")
        return None
