"""Federal tax calculator for Form 1040."""
from ..models.tax_return import TaxReturn, FilingStatus
from .tax_brackets import (
    load_tax_tables,
    calculate_tax_by_bracket,
    get_standard_deduction,
    get_tax_brackets,
)


class FederalCalculator:
    """Calculator for federal taxes (Form 1040)."""

    def __init__(self, tax_year: int = 2025):
        """
        Initialize the federal tax calculator.

        Args:
            tax_year: Tax year to calculate for
        """
        self.tax_year = tax_year
        self.tax_tables = load_tax_tables(tax_year)

    def calculate(self, tax_return: TaxReturn) -> dict:
        """
        Calculate federal taxes for a tax return.

        Args:
            tax_return: TaxReturn object with income and deduction information

        Returns:
            Dictionary with calculated federal tax values
        """
        results = {
            'gross_income': 0.0,
            'total_income': 0.0,
            'adjustments': 0.0,
            'agi': 0.0,
            'deductions': 0.0,
            'taxable_income': 0.0,
            'tax': 0.0,
            'tax_withheld': 0.0,
            'refund_or_owed': 0.0,
        }

        # Convert filing status to table key
        filing_status_key = tax_return.filing_status.value

        # Step 1: Calculate gross income
        wages = tax_return.get_total_wages()
        income_1099 = tax_return.get_total_1099_income()
        results['gross_income'] = wages + income_1099

        # Step 2: Total income (same as gross income for basic 1040)
        results['total_income'] = results['gross_income']

        # Step 3: Calculate adjustments
        adjustments = (
            tax_return.traditional_ira_contributions +
            tax_return.student_loan_interest +
            tax_return.hsa_contributions +
            tax_return.other_adjustments
        )
        results['adjustments'] = adjustments

        # Step 4: Calculate AGI (Adjusted Gross Income)
        results['agi'] = max(0, results['total_income'] - adjustments)

        # Step 5: Calculate deductions
        if tax_return.use_standard_deduction:
            results['deductions'] = get_standard_deduction(
                self.tax_tables,
                filing_status_key,
                'federal'
            )
        else:
            results['deductions'] = tax_return.itemized_deductions

        # Step 6: Calculate taxable income
        results['taxable_income'] = max(0, results['agi'] - results['deductions'])

        # Step 7: Calculate tax using brackets
        brackets = get_tax_brackets(self.tax_tables, filing_status_key, 'federal')
        if brackets:
            results['tax'] = calculate_tax_by_bracket(results['taxable_income'], brackets)
        else:
            results['tax'] = 0.0

        # Step 8: Calculate tax withheld
        w2_withheld = tax_return.get_total_federal_tax_withheld_w2()
        income_1099_withheld = tax_return.get_total_federal_tax_withheld_1099()
        results['tax_withheld'] = w2_withheld + income_1099_withheld

        # Step 9: Calculate refund or amount owed
        results['refund_or_owed'] = results['tax_withheld'] - results['tax']

        return results

    def update_tax_return(self, tax_return: TaxReturn) -> None:
        """
        Update a TaxReturn object with calculated federal tax values.

        Args:
            tax_return: TaxReturn object to update
        """
        results = self.calculate(tax_return)

        tax_return.federal_gross_income = results['gross_income']
        tax_return.federal_total_income = results['total_income']
        tax_return.federal_agi = results['agi']
        tax_return.federal_taxable_income = results['taxable_income']
        tax_return.federal_tax = results['tax']
        tax_return.federal_tax_withheld = results['tax_withheld']
        tax_return.federal_refund_or_owed = results['refund_or_owed']


def calculate_federal_taxes(tax_return: TaxReturn, tax_year: int = 2025) -> dict:
    """
    Convenience function to calculate federal taxes.

    Args:
        tax_return: TaxReturn object
        tax_year: Tax year

    Returns:
        Dictionary with calculated federal tax values
    """
    calculator = FederalCalculator(tax_year)
    calculator.update_tax_return(tax_return)
    return {
        'gross_income': tax_return.federal_gross_income,
        'total_income': tax_return.federal_total_income,
        'agi': tax_return.federal_agi,
        'taxable_income': tax_return.federal_taxable_income,
        'tax': tax_return.federal_tax,
        'tax_withheld': tax_return.federal_tax_withheld,
        'refund_or_owed': tax_return.federal_refund_or_owed,
    }
