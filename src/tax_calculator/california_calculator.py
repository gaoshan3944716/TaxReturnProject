"""California state tax calculator (Form 540)."""
from ..models.tax_return import TaxReturn, FilingStatus
from .tax_brackets import (
    load_tax_tables,
    calculate_tax_by_bracket,
    get_standard_deduction,
    get_tax_brackets,
)


class CaliforniaCalculator:
    """Calculator for California state taxes (Form 540)."""

    def __init__(self, tax_year: int = 2025):
        """
        Initialize the California tax calculator.

        Args:
            tax_year: Tax year to calculate for
        """
        self.tax_year = tax_year
        self.tax_tables = load_tax_tables(tax_year)

    def calculate(self, tax_return: TaxReturn) -> dict:
        """
        Calculate California state taxes for a tax return.

        Args:
            tax_return: TaxReturn object with income and deduction information

        Returns:
            Dictionary with calculated California tax values
        """
        results = {
            'gross_income': 0.0,
            'federal_agi': 0.0,
            'agi': 0.0,
            'deductions': 0.0,
            'taxable_income': 0.0,
            'tax': 0.0,
            'tax_withheld': 0.0,
            'sdi_withheld': 0.0,
            'refund_or_owed': 0.0,
        }

        # Convert filing status to table key
        filing_status_key = tax_return.filing_status.value

        # Step 1: Start with federal AGI
        results['federal_agi'] = tax_return.federal_agi

        # Step 2: Calculate CA AGI (simplified - same as federal AGI for basic cases)
        # In reality, there would be CA-specific adjustments
        results['agi'] = results['federal_agi']

        # Step 3: Calculate deductions
        if tax_return.use_standard_deduction:
            results['deductions'] = get_standard_deduction(
                self.tax_tables,
                filing_status_key,
                'california'
            )
        else:
            # For itemized deductions, CA has different rules
            results['deductions'] = tax_return.itemized_deductions

        # Step 4: Calculate taxable income
        results['taxable_income'] = max(0, results['agi'] - results['deductions'])

        # Step 5: Calculate tax using CA brackets
        brackets = get_tax_brackets(self.tax_tables, filing_status_key, 'california')
        if brackets:
            results['tax'] = calculate_tax_by_bracket(results['taxable_income'], brackets)
        else:
            results['tax'] = 0.0

        # Step 6: Calculate tax withheld
        results['tax_withheld'] = tax_return.get_total_ca_tax_withheld_w2()
        results['sdi_withheld'] = tax_return.get_total_ca_sdi_withheld_w2()

        # Step 7: Calculate refund or amount owed
        total_withheld = results['tax_withheld'] + results['sdi_withheld']
        results['refund_or_owed'] = total_withheld - results['tax']

        return results

    def update_tax_return(self, tax_return: TaxReturn) -> None:
        """
        Update a TaxReturn object with calculated California tax values.

        Args:
            tax_return: TaxReturn object to update
        """
        results = self.calculate(tax_return)

        tax_return.ca_gross_income = tax_return.federal_gross_income
        tax_return.ca_agi = results['agi']
        tax_return.ca_taxable_income = results['taxable_income']
        tax_return.ca_tax = results['tax']
        tax_return.ca_tax_withheld = results['tax_withheld']
        tax_return.ca_sdi_withheld = results['sdi_withheld']
        tax_return.ca_refund_or_owed = results['refund_or_owed']


def calculate_california_taxes(tax_return: TaxReturn, tax_year: int = 2025) -> dict:
    """
    Convenience function to calculate California state taxes.

    Args:
        tax_return: TaxReturn object
        tax_year: Tax year

    Returns:
        Dictionary with calculated California tax values
    """
    calculator = CaliforniaCalculator(tax_year)
    calculator.update_tax_return(tax_return)
    return {
        'gross_income': tax_return.ca_gross_income,
        'agi': tax_return.ca_agi,
        'taxable_income': tax_return.ca_taxable_income,
        'tax': tax_return.ca_tax,
        'tax_withheld': tax_return.ca_tax_withheld,
        'sdi_withheld': tax_return.ca_sdi_withheld,
        'refund_or_owed': tax_return.ca_refund_or_owed,
    }


def calculate_all_taxes(tax_return: TaxReturn, tax_year: int = 2025) -> None:
    """
    Calculate both federal and California taxes for a tax return.

    Args:
        tax_return: TaxReturn object to update
        tax_year: Tax year
    """
    from .federal_calculator import FederalCalculator

    federal_calc = FederalCalculator(tax_year)
    ca_calc = CaliforniaCalculator(tax_year)

    federal_calc.update_tax_return(tax_return)
    ca_calc.update_tax_return(tax_return)
