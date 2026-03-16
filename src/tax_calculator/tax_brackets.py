"""Tax bracket definitions and utilities."""
import json
from pathlib import Path
from typing import Optional


def load_tax_tables(year: int = 2025) -> dict:
    """
    Load tax tables from JSON files.

    Args:
        year: Tax year to load tables for

    Returns:
        Dictionary containing federal and California tax tables
    """
    base_dir = Path(__file__).parent.parent.parent
    data_dir = base_dir / "data" / "tax_tables"

    tables = {}

    try:
        with open(data_dir / f"federal_{year}.json", "r") as f:
            tables['federal'] = json.load(f)
    except FileNotFoundError:
        print(f"Federal tax table for {year} not found")

    try:
        with open(data_dir / f"california_{year}.json", "r") as f:
            tables['california'] = json.load(f)
    except FileNotFoundError:
        print(f"California tax table for {year} not found")

    return tables


def calculate_tax_by_bracket(taxable_income: float, brackets: list[dict]) -> float:
    """
    Calculate tax using progressive tax brackets.

    Args:
        taxable_income: Income to calculate tax on
        brackets: List of bracket dictionaries with 'min', 'max', and 'rate'

    Returns:
        Total tax calculated
    """
    total_tax = 0.0
    remaining_income = taxable_income

    for bracket in brackets:
        bracket_min = bracket['min']
        bracket_max = bracket['max'] if bracket['max'] is not None else float('inf')
        rate = bracket['rate']

        if remaining_income <= 0:
            break

        # Income in this bracket
        bracket_width = bracket_max - bracket_min
        income_in_bracket = min(remaining_income, bracket_width)

        if taxable_income > bracket_min:
            # Calculate tax for income in this bracket
            if taxable_income > bracket_max:
                # Income spans entire bracket
                total_tax += bracket_width * rate
            else:
                # Income ends in this bracket
                total_tax += (taxable_income - bracket_min) * rate

    return total_tax


def get_standard_deduction(tax_tables: dict, filing_status: str,
                           jurisdiction: str = 'federal') -> float:
    """
    Get standard deduction for a filing status.

    Args:
        tax_tables: Tax tables dictionary
        filing_status: Filing status (single, married_filing_jointly, etc.)
        jurisdiction: Either 'federal' or 'california'

    Returns:
        Standard deduction amount
    """
    try:
        return tax_tables[jurisdiction]['standard_deduction'].get(filing_status, 0)
    except (KeyError, TypeError):
        return 0.0


def get_tax_brackets(tax_tables: dict, filing_status: str,
                     jurisdiction: str = 'federal') -> Optional[list[dict]]:
    """
    Get tax brackets for a filing status.

    Args:
        tax_tables: Tax tables dictionary
        filing_status: Filing status (single, married_filing_jointly, etc.)
        jurisdiction: Either 'federal' or 'california'

    Returns:
        List of tax bracket dictionaries
    """
    try:
        return tax_tables[jurisdiction]['tax_brackets'].get(filing_status, [])
    except (KeyError, TypeError):
        return None
