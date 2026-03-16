"""Form 1099 PDF parser."""
import re
from typing import Optional, Tuple, Union
from .base_parser import BasePDFParser
from ..models.form1099 import Form1099NEC, Form1099INT, Form1099DIV


class Form1099Parser(BasePDFParser):
    """Parser for various 1099 forms."""

    FORM_KEYWORDS = {
        '1099-NEC': ['1099-nec', 'nonemployee compensation', 'form 1099 nec'],
        '1099-INT': ['1099-int', 'interest income', 'form 1099 int'],
        '1099-DIV': ['1099-div', 'dividends', 'form 1099 div'],
    }

    def validate_pdf(self) -> Tuple[bool, str]:
        """Validate that the PDF is a 1099 form and identify the type."""
        is_valid, error = super().validate_pdf()
        if not is_valid:
            return is_valid, error

        text = self.get_text(0).lower()

        # Identify form type
        for form_type, keywords in self.FORM_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                return True, form_type

        return False, "PDF does not appear to be a 1099 form"

    def identify_form_type(self) -> Optional[str]:
        """Identify which type of 1099 form this is."""
        text = self.get_text(0).lower()

        for form_type, keywords in self.FORM_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                return form_type

        return None

    def parse(self) -> Optional[Union[Form1099NEC, Form1099INT, Form1099DIV]]:
        """
        Parse the 1099 PDF and return the appropriate form object.

        Returns:
            Form1099NEC, Form1099INT, or Form1099DIV object, or None if parsing fails
        """
        form_type = self.identify_form_type()

        if form_type == '1099-NEC':
            return self._parse_1099_nec()
        elif form_type == '1099-INT':
            return self._parse_1099_int()
        elif form_type == '1099-DIV':
            return self._parse_1099_div()
        else:
            return None

    def _parse_1099_nec(self) -> Form1099NEC:
        """Parse a 1099-NEC form."""
        form = Form1099NEC()

        # Get all text from the PDF
        all_text = ""
        for i in range(len(self.pages)):
            all_text += self.get_text(i) + "\n"

        # Extract common fields
        form = self._extract_payer_info(form, all_text)
        form = self._extract_recipient_info(form, all_text)

        # Extract box values for 1099-NEC
        form = self._extract_box_values_1099_nec(form, all_text)

        return form

    def _parse_1099_int(self) -> Form1099INT:
        """Parse a 1099-INT form."""
        form = Form1099INT()

        # Get all text from the PDF
        all_text = ""
        for i in range(len(self.pages)):
            all_text += self.get_text(i) + "\n"

        # Extract common fields
        form = self._extract_payer_info(form, all_text)
        form = self._extract_recipient_info(form, all_text)

        # Extract box values for 1099-INT
        form = self._extract_box_values_1099_int(form, all_text)

        return form

    def _parse_1099_div(self) -> Form1099DIV:
        """Parse a 1099-DIV form."""
        form = Form1099DIV()

        # Get all text from the PDF
        all_text = ""
        for i in range(len(self.pages)):
            all_text += self.get_text(i) + "\n"

        # Extract common fields
        form = self._extract_payer_info(form, all_text)
        form = self._extract_recipient_info(form, all_text)

        # Extract box values for 1099-DIV
        form = self._extract_box_values_1099_div(form, all_text)

        return form

    def _extract_payer_info(self, form: Union[Form1099NEC, Form1099INT, Form1099DIV],
                            text: str) -> Union[Form1099NEC, Form1099INT, Form1099DIV]:
        """Extract payer information."""
        lines = text.split('\n')

        # Look for payer information
        for i, line in enumerate(lines):
            if 'payer' in line.lower() and 'name' in line.lower():
                if i + 1 < len(lines) and lines[i + 1].strip():
                    form.payer_name = lines[i + 1].strip()

        # Look for EIN (9 digits, possibly with dashes)
        ein_pattern = r'(\d{2}-\d{7}|\d{9})'
        ein_matches = re.findall(ein_pattern, text)
        if ein_matches:
            form.payer_ein = ein_matches[0]

        return form

    def _extract_recipient_info(self, form: Union[Form1099NEC, Form1099INT, Form1099DIV],
                                 text: str) -> Union[Form1099NEC, Form1099INT, Form1099DIV]:
        """Extract recipient information."""
        lines = text.split('\n')

        # Look for recipient name
        for i, line in enumerate(lines):
            if 'recipient' in line.lower() and 'name' in line.lower():
                if i + 1 < len(lines) and lines[i + 1].strip():
                    form.recipient_name = lines[i + 1].strip()

        return form

    def _extract_box_values_1099_nec(self, form: Form1099NEC,
                                      text: str) -> Form1099NEC:
        """Extract box values specific to 1099-NEC."""
        # Look for monetary values in the text
        amounts = re.findall(r'\$?\s*([0-9,]+\.?\d*)\s*\$?', text)

        # Try to identify which amounts go in which boxes
        # This is simplified - real implementation would need coordinate mapping

        # Nonemployee compensation (Box 1) - typically the largest amount
        if amounts:
            amounts_float = [float(a.replace(',', '')) for a in amounts if a]
            if amounts_float:
                form.box1_nonemployee_compensation = max(amounts_float)

        return form

    def _extract_box_values_1099_int(self, form: Form1099INT,
                                      text: str) -> Form1099INT:
        """Extract box values specific to 1099-INT."""
        # Look for interest income pattern
        interest_pattern = r'interest\s*(income)?\s*[:\s]+\$?\s*([0-9,]+\.?\d*)'
        match = re.search(interest_pattern, text, re.IGNORECASE)
        if match:
            try:
                form.box1_interest_income = float(match.group(2).replace(',', ''))
            except ValueError:
                pass

        # Try to find any monetary values
        amounts = re.findall(r'\$?\s*([0-9,]+\.?\d*)\s*\$?', text)
        if amounts:
            amounts_float = [float(a.replace(',', '')) for a in amounts if a]
            if amounts_float and form.box1_interest_income == 0:
                form.box1_interest_income = max(amounts_float)

        return form

    def _extract_box_values_1099_div(self, form: Form1099DIV,
                                      text: str) -> Form1099DIV:
        """Extract box values specific to 1099-DIV."""
        # Look for dividend patterns
        div_patterns = [
            r'dividend.*\$?\s*([0-9,]+\.?\d*)',
            r'ordinary\s*dividend.*\$?\s*([0-9,]+\.?\d*)',
        ]

        for pattern in div_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    form.box1a_total_ordinary_dividends = float(match.group(1).replace(',', ''))
                    break
                except ValueError:
                    pass

        # Try to find any monetary values
        amounts = re.findall(r'\$?\s*([0-9,]+\.?\d*)\s*\$?', text)
        if amounts:
            amounts_float = [float(a.replace(',', '')) for a in amounts if a]
            if amounts_float and form.box1a_total_ordinary_dividends == 0:
                form.box1a_total_ordinary_dividends = max(amounts_float)

        return form


def parse_1099_pdf(pdf_path: str) -> Optional[Union[Form1099NEC, Form1099INT, Form1099DIV]]:
    """
    Parse a 1099 PDF file and return the appropriate form object.

    Args:
        pdf_path: Path to the 1099 PDF file

    Returns:
        Form1099NEC, Form1099INT, or Form1099DIV object, or None if parsing fails
    """
    try:
        parser = Form1099Parser(pdf_path)
        return parser.parse()
    except Exception as e:
        print(f"Error parsing 1099 PDF: {e}")
        return None
