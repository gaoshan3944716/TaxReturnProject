"""Summary report generator."""
from datetime import datetime
from typing import Optional
from ..models.tax_return import TaxReturn


class SummaryGenerator:
    """Generator for tax return summary report."""

    def __init__(self, tax_return: TaxReturn):
        """
        Initialize the summary generator.

        Args:
            tax_return: TaxReturn object with calculated tax values
        """
        self.tax_return = tax_return

    def generate_text(self) -> str:
        """
        Generate summary report as text.

        Returns:
            Text summary of the tax return
        """
        lines = []

        # Header
        lines.append("=" * 70)
        lines.append(f"TAX RETURN SUMMARY - {self.tax_return.tax_year}")
        lines.append("=" * 70)
        lines.append("")

        # Personal Info
        lines.append("PERSONAL INFORMATION")
        lines.append("-" * 70)
        info = self.tax_return.personal_info
        lines.append(f"Name: {info.first_name} {info.middle_initial} {info.last_name}")
        lines.append(f"Address: {info.street_address}")
        lines.append(f"         {info.city}, {info.state} {info.zip_code}")
        lines.append(f"Filing Status: {self.tax_return.filing_status.value.replace('_', ' ').title()}")
        lines.append("")

        # Income Summary
        lines.append("INCOME SUMMARY")
        lines.append("-" * 70)
        lines.append(f"Total Wages (W-2):        {self._format_currency(self.tax_return.get_total_wages())}")
        lines.append(f"Total 1099 Income:        {self._format_currency(self.tax_return.get_total_1099_income())}")
        lines.append(f"Total Gross Income:      {self._format_currency(self.tax_return.federal_gross_income)}")
        lines.append(f"Total Income:            {self._format_currency(self.tax_return.federal_total_income)}")
        lines.append(f"Adjusted Gross Income:   {self._format_currency(self.tax_return.federal_agi)}")
        lines.append("")

        # Deductions
        if self.tax_return.use_standard_deduction:
            lines.append("DEDUCTIONS")
            lines.append("-" * 70)
            lines.append(f"Standard Deduction:     {self._format_currency(self._get_federal_std_ded())}")
        else:
            lines.append("DEDUCTIONS")
            lines.append("-" * 70)
            lines.append(f"Itemized Deductions:    {self._format_currency(self.tax_return.itemized_deductions)}")
        lines.append(f"Taxable Income:         {self._format_currency(self.tax_return.federal_taxable_income)}")
        lines.append("")

        # Adjustments
        adjustments = (
            self.tax_return.traditional_ira_contributions +
            self.tax_return.student_loan_interest +
            self.tax_return.hsa_contributions +
            self.tax_return.other_adjustments
        )
        if adjustments > 0:
            lines.append("INCOME ADJUSTMENTS")
            lines.append("-" * 70)
            if self.tax_return.traditional_ira_contributions > 0:
                lines.append(f"Traditional IRA:         {self._format_currency(self.tax_return.traditional_ira_contributions)}")
            if self.tax_return.student_loan_interest > 0:
                lines.append(f"Student Loan Interest:   {self._format_currency(self.tax_return.student_loan_interest)}")
            if self.tax_return.hsa_contributions > 0:
                lines.append(f"HSA Contributions:       {self._format_currency(self.tax_return.hsa_contributions)}")
            if self.tax_return.other_adjustments > 0:
                lines.append(f"Other Adjustments:       {self._format_currency(self.tax_return.other_adjustments)}")
            lines.append("")

        # Federal Tax
        lines.append("FEDERAL TAX (Form 1040)")
        lines.append("-" * 70)
        lines.append(f"Tax:                    {self._format_currency(self.tax_return.federal_tax)}")
        lines.append(f"Tax Withheld:           {self._format_currency(self.tax_return.federal_tax_withheld)}")
        lines.append("")

        if self.tax_return.federal_refund_or_owed > 0:
            lines.append(f"FEDERAL REFUND:         {self._format_currency(self.tax_return.federal_refund_or_owed)}")
        else:
            lines.append(f"FEDERAL AMOUNT OWED:    {self._format_currency(abs(self.tax_return.federal_refund_or_owed))}")
        lines.append("")

        # California Tax
        lines.append("CALIFORNIA STATE TAX (Form 540)")
        lines.append("-" * 70)
        lines.append(f"Tax:                    {self._format_currency(self.tax_return.ca_tax)}")
        lines.append(f"Tax Withheld:           {self._format_currency(self.tax_return.ca_tax_withheld)}")
        lines.append(f"SDI Withheld:           {self._format_currency(self.tax_return.ca_sdi_withheld)}")
        total_ca_withheld = self.tax_return.ca_tax_withheld + self.tax_return.ca_sdi_withheld
        lines.append(f"Total Withheld:         {self._format_currency(total_ca_withheld)}")
        lines.append("")

        if self.tax_return.ca_refund_or_owed > 0:
            lines.append(f"CA STATE REFUND:        {self._format_currency(self.tax_return.ca_refund_or_owed)}")
        else:
            lines.append(f"CA STATE AMOUNT OWED:   {self._format_currency(abs(self.tax_return.ca_refund_or_owed))}")
        lines.append("")

        # Summary Table
        lines.append("SUMMARY")
        lines.append("-" * 70)
        fed_amount = abs(self.tax_return.federal_refund_or_owed)
        ca_amount = abs(self.tax_return.ca_refund_or_owed)

        if self.tax_return.federal_refund_or_owed > 0:
            lines.append(f"Federal Refund:         {self._format_currency(self.tax_return.federal_refund_or_owed)}")
        else:
            lines.append(f"Federal Owed:           {self._format_currency(self.tax_return.federal_refund_or_owed)}")

        if self.tax_return.ca_refund_or_owed > 0:
            lines.append(f"California Refund:      {self._format_currency(self.tax_return.ca_refund_or_owed)}")
        else:
            lines.append(f"California Owed:        {self._format_currency(self.tax_return.ca_refund_or_owed)}")

        if self.tax_return.federal_refund_or_owed > 0 and self.tax_return.ca_refund_or_owed > 0:
            total_refund = self.tax_return.federal_refund_or_owed + self.tax_return.ca_refund_or_owed
            lines.append(f"TOTAL REFUND:           {self._format_currency(total_refund)}")
        elif self.tax_return.federal_refund_or_owed < 0 and self.tax_return.ca_refund_or_owed < 0:
            total_owed = abs(self.tax_return.federal_refund_or_owed + self.tax_return.ca_refund_or_owed)
            lines.append(f"TOTAL OWED:             {self._format_currency(total_owed)}")

        lines.append("")
        lines.append("=" * 70)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("DISCLAIMER: This is an estimate. For official tax filing, please use")
        lines.append("IRS-approved software or consult a tax professional.")
        lines.append("=" * 70)

        return "\n".join(lines)

    def generate_html(self) -> str:
        """
        Generate summary report as HTML.

        Returns:
            HTML summary of the tax return
        """
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Tax Return Summary</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 20px auto; }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; }
        h2 { color: #34495e; margin-top: 30px; }
        .section { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #dee2e6; }
        .row:last-child { border-bottom: none; }
        .label { font-weight: bold; }
        .value { font-family: 'Courier New', monospace; }
        .refund { color: #27ae60; font-weight: bold; font-size: 1.1em; }
        .owed { color: #e74c3c; font-weight: bold; font-size: 1.1em; }
        .disclaimer { font-size: 0.85em; color: #7f8c8d; margin-top: 30px; padding: 10px; background: #fff3cd; border-radius: 5px; }
    </style>
</head>
<body>
"""

        # Header
        html += f"<h1>Tax Return Summary - {self.tax_return.tax_year}</h1>\n"

        # Personal Info
        info = self.tax_return.personal_info
        html += """
    <h2>Personal Information</h2>
    <div class="section">
        <div class="row"><span class="label">Name:</span><span class="value">{0} {1} {2}</span></div>
        <div class="row"><span class="label">Address:</span><span class="value">{3}</span></div>
        <div class="row"><span class="label">City/State/Zip:</span><span class="value">{4}, {5} {6}</span></div>
        <div class="row"><span class="label">Filing Status:</span><span class="value">{7}</span></div>
    </div>
""".format(
            info.first_name, info.middle_initial, info.last_name,
            info.street_address,
            info.city, info.state, info.zip_code,
            self.tax_return.filing_status.value.replace('_', ' ').title()
        )

        # Income
        html += f"""
    <h2>Income</h2>
    <div class="section">
        <div class="row"><span class="label">Total Wages (W-2):</span><span class="value">{self._format_currency(self.tax_return.get_total_wages())}</span></div>
        <div class="row"><span class="label">Total 1099 Income:</span><span class="value">{self._format_currency(self.tax_return.get_total_1099_income())}</span></div>
        <div class="row"><span class="label">Gross Income:</span><span class="value">{self._format_currency(self.tax_return.federal_gross_income)}</span></div>
        <div class="row"><span class="label">Adjusted Gross Income:</span><span class="value">{self._format_currency(self.tax_return.federal_agi)}</span></div>
        <div class="row"><span class="label">Taxable Income:</span><span class="value">{self._format_currency(self.tax_return.federal_taxable_income)}</span></div>
    </div>
"""

        # Federal Tax
        fed_class = "refund" if self.tax_return.federal_refund_or_owed > 0 else "owed"
        fed_label = "Federal Refund" if self.tax_return.federal_refund_or_owed > 0 else "Federal Amount Owed"
        html += f"""
    <h2>Federal Tax (Form 1040)</h2>
    <div class="section">
        <div class="row"><span class="label">Tax:</span><span class="value">{self._format_currency(self.tax_return.federal_tax)}</span></div>
        <div class="row"><span class="label">Tax Withheld:</span><span class="value">{self._format_currency(self.tax_return.federal_tax_withheld)}</span></div>
        <div class="row"><span class="label">{fed_label}:</span><span class="value {fed_class}">{self._format_currency(abs(self.tax_return.federal_refund_or_owed))}</span></div>
    </div>
"""

        # California Tax
        ca_class = "refund" if self.tax_return.ca_refund_or_owed > 0 else "owed"
        ca_label = "CA State Refund" if self.tax_return.ca_refund_or_owed > 0 else "CA State Amount Owed"
        html += f"""
    <h2>California State Tax (Form 540)</h2>
    <div class="section">
        <div class="row"><span class="label">Tax:</span><span class="value">{self._format_currency(self.tax_return.ca_tax)}</span></div>
        <div class="row"><span class="label">Tax Withheld:</span><span class="value">{self._format_currency(self.tax_return.ca_tax_withheld)}</span></div>
        <div class="row"><span class="label">SDI Withheld:</span><span class="value">{self._format_currency(self.tax_return.ca_sdi_withheld)}</span></div>
        <div class="row"><span class="label">{ca_label}:</span><span class="value {ca_class}">{self._format_currency(abs(self.tax_return.ca_refund_or_owed))}</span></div>
    </div>
"""

        # Disclaimer
        html += f"""
    <div class="disclaimer">
        <strong>DISCLAIMER:</strong> This is an estimate generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.
        For official tax filing, please use IRS-approved software or consult a tax professional.
    </div>
</body>
</html>
"""
        return html

    def save_text(self, output_path: str) -> None:
        """
        Save summary report as text file.

        Args:
            output_path: Path where the text file will be saved
        """
        with open(output_path, 'w') as f:
            f.write(self.generate_text())

    def save_html(self, output_path: str) -> None:
        """
        Save summary report as HTML file.

        Args:
            output_path: Path where the HTML file will be saved
        """
        with open(output_path, 'w') as f:
            f.write(self.generate_html())

    def _format_currency(self, amount: float) -> str:
        """Format amount as currency."""
        return f"${amount:,.2f}"

    def _get_federal_std_ded(self) -> float:
        """Get federal standard deduction amount."""
        deductions = {
            'single': 14600,
            'married_filing_jointly': 29200,
            'married_filing_separately': 14600,
            'head_of_household': 21900,
        }
        return deductions.get(self.tax_return.filing_status.value, 0)


def generate_summary_report(tax_return: TaxReturn, output_path: str, format: str = 'text') -> None:
    """
    Generate summary report for a tax return.

    Args:
        tax_return: TaxReturn object with calculated tax values
        output_path: Path where the report will be saved
        format: Either 'text' or 'html'
    """
    generator = SummaryGenerator(tax_return)
    if format == 'html':
        generator.save_html(output_path)
    else:
        generator.save_text(output_path)
