"""PDF generator for IRS Form 1040."""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
from typing import Optional
from ..models.tax_return import TaxReturn


class Form1040Generator:
    """Generator for IRS Form 1040 PDF."""

    def __init__(self, tax_return: TaxReturn):
        """
        Initialize the Form 1040 generator.

        Args:
            tax_return: TaxReturn object with calculated tax values
        """
        self.tax_return = tax_return
        self.width = letter[0]
        self.height = letter[1]
        self.margin = 0.5 * inch

    def generate(self, output_path: str) -> None:
        """
        Generate Form 1040 PDF file.

        Args:
            output_path: Path where the PDF will be saved
        """
        c = canvas.Canvas(output_path, pagesize=letter)

        # Draw form header
        self._draw_header(c)

        # Draw personal info section
        self._draw_personal_info(c)

        # Draw income section
        self._draw_income_section(c)

        # Draw deductions section
        self._draw_deductions_section(c)

        # Draw tax calculations section
        self._draw_tax_calculations(c)

        # Draw signature section
        self._draw_signature_section(c)

        # Add disclaimer
        self._draw_disclaimer(c)

        c.save()

    def _draw_header(self, c: canvas.Canvas) -> None:
        """Draw form header."""
        c.setFont("Helvetica-Bold", 16)
        c.drawString(self.margin, self.height - self.margin,
                     f"Form 1040 - {self.tax_return.tax_year}")
        c.setFont("Helvetica", 10)
        c.drawString(self.margin, self.height - self.margin - 15,
                     "U.S. Individual Income Tax Return")

    def _draw_personal_info(self, c: canvas.Canvas) -> None:
        """Draw personal information section."""
        y = self.height - self.margin - 50

        # Personal info label
        c.setFont("Helvetica-Bold", 11)
        c.drawString(self.margin, y, "Personal Information")

        # Name
        y -= 20
        c.setFont("Helvetica", 10)
        c.drawString(self.margin, y,
                     f"Name: {self.tax_return.personal_info.first_name} "
                     f"{self.tax_return.personal_info.middle_initial} "
                     f"{self.tax_return.personal_info.last_name}")

        # SSN
        y -= 15
        c.drawString(self.margin, y,
                     f"SSN: {self._mask_ssn(self.tax_return.personal_info.ssn)}")

        # Address
        y -= 15
        c.drawString(self.margin, y,
                     f"Address: {self.tax_return.personal_info.street_address}")
        y -= 12
        c.drawString(self.margin, y,
                     f"         {self.tax_return.personal_info.city}, "
                     f"{self.tax_return.personal_info.state} "
                     f"{self.tax_return.personal_info.zip_code}")

        # Filing status
        y -= 20
        c.setFont("Helvetica-Bold", 10)
        c.drawString(self.margin, y, "Filing Status:")
        c.setFont("Helvetica", 10)
        y -= 15
        c.drawString(self.margin + 20, y,
                     self.tax_return.filing_status.value.replace('_', ' ').title())

    def _draw_income_section(self, c: canvas.Canvas) -> None:
        """Draw income section."""
        y = self.height - 3 * inch

        c.setFont("Helvetica-Bold", 11)
        c.drawString(self.margin, y, "Income")

        y -= 25
        c.setFont("Helvetica", 10)
        c.drawString(self.margin, y, "1. Wages, salaries, tips, etc.")
        c.drawString(5 * inch, y, self._format_currency(self.tax_return.get_total_wages()))

        y -= 15
        c.drawString(self.margin, y, "2. Interest income")
        c.drawString(5 * inch, y, self._format_currency(0.0))  # Simplified

        y -= 15
        c.drawString(self.margin, y, "3a. Total income")
        c.drawString(5 * inch, y, self._format_currency(self.tax_return.federal_total_income))

    def _draw_deductions_section(self, c: canvas.Canvas) -> None:
        """Draw deductions section."""
        y = self.height - 4.5 * inch

        c.setFont("Helvetica-Bold", 11)
        c.drawString(self.margin, y, "Deductions")

        y -= 25
        c.setFont("Helvetica", 10)
        if self.tax_return.use_standard_deduction:
            c.drawString(self.margin, y, "8. Standard deduction")
            c.drawString(5 * inch, y, self._format_currency(
                self._get_standard_deduction()))
        else:
            c.drawString(self.margin, y, "8. Itemized deductions")
            c.drawString(5 * inch, y, self._format_currency(
                self.tax_return.itemized_deductions))

        y -= 15
        c.drawString(self.margin, y, "9. Taxable income")
        c.drawString(5 * inch, y, self._format_currency(
            self.tax_return.federal_taxable_income))

    def _draw_tax_calculations(self, c: canvas.Canvas) -> None:
        """Draw tax calculations section."""
        y = self.height - 5.5 * inch

        c.setFont("Helvetica-Bold", 11)
        c.drawString(self.margin, y, "Tax")

        y -= 25
        c.setFont("Helvetica", 10)
        c.drawString(self.margin, y, "10. Tax")
        c.drawString(5 * inch, y, self._format_currency(self.tax_return.federal_tax))

        y -= 15
        c.drawString(self.margin, y, "11. Total tax")
        c.drawString(5 * inch, y, self._format_currency(self.tax_return.federal_tax))

        # Payments section
        y -= 25
        c.setFont("Helvetica-Bold", 11)
        c.drawString(self.margin, y, "Payments")

        y -= 25
        c.setFont("Helvetica", 10)
        c.drawString(self.margin, y, "15. Federal income tax withheld")
        c.drawString(5 * inch, y, self._format_currency(
            self.tax_return.federal_tax_withheld))

        y -= 15
        c.drawString(self.margin, y, "24. Total payments")
        c.drawString(5 * inch, y, self._format_currency(
            self.tax_return.federal_tax_withheld))

        # Refund or amount owed
        y -= 30
        c.setFont("Helvetica-Bold", 11)
        c.drawString(self.margin, y, "Refund")

        y -= 25
        c.setFont("Helvetica", 10)
        if self.tax_return.federal_refund_or_owed > 0:
            c.drawString(self.margin, y, "32. Refund")
            c.drawString(5 * inch, y, self._format_currency(
                self.tax_return.federal_refund_or_owed))
        else:
            c.setFont("Helvetica-Bold", 11)
            c.drawString(self.margin, y, "Amount You Owe")
            y -= 25
            c.setFont("Helvetica", 10)
            c.drawString(self.margin, y, "37. Amount you owe")
            c.drawString(5 * inch, y, self._format_currency(
                abs(self.tax_return.federal_refund_or_owed)))

    def _draw_signature_section(self, c: canvas.Canvas) -> None:
        """Draw signature section."""
        y = 1.5 * inch

        c.setFont("Helvetica-Bold", 10)
        c.drawString(self.margin, y, "Sign Here")

        y -= 25
        c.setFont("Helvetica", 9)
        c.drawString(self.margin, y,
                     f"Your signature: ______________________________  Date: _____/_____/_____")

        y -= 15
        c.drawString(self.margin, y,
                     f"Spouse signature: ____________________________  Date: _____/_____/_____")

    def _draw_disclaimer(self, c: canvas.Canvas) -> None:
        """Draw disclaimer at bottom of page."""
        y = 0.75 * inch

        c.setFont("Helvetica", 8)
        disclaimer = (
            "DISCLAIMER: This is a generated form for informational purposes only. "
            "For official tax filing, please use IRS-approved software or consult a tax professional."
        )
        c.drawString(self.margin, y, disclaimer)

    def _format_currency(self, amount: float) -> str:
        """Format amount as currency."""
        return f"${amount:,.2f}"

    def _mask_ssn(self, ssn: str) -> str:
        """Mask SSN for privacy."""
        if len(ssn) >= 9:
            clean = ssn.replace('-', '')
            return f"***-**-{clean[-4:]}"
        return "***-**-****"

    def _get_standard_deduction(self) -> float:
        """Get standard deduction amount."""
        # These match the values in federal_2025.json
        deductions = {
            'single': 14600,
            'married_filing_jointly': 29200,
            'married_filing_separately': 14600,
            'head_of_household': 21900,
        }
        return deductions.get(self.tax_return.filing_status.value, 0)


def generate_form1040_pdf(tax_return: TaxReturn, output_path: str) -> None:
    """
    Generate Form 1040 PDF for a tax return.

    Args:
        tax_return: TaxReturn object with calculated tax values
        output_path: Path where the PDF will be saved
    """
    generator = Form1040Generator(tax_return)
    generator.generate(output_path)
