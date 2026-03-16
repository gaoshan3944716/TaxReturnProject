"""Tax calculator module for federal and California taxes."""
from .tax_brackets import (
    load_tax_tables,
    calculate_tax_by_bracket,
    get_standard_deduction,
    get_tax_brackets,
)
from .federal_calculator import FederalCalculator, calculate_federal_taxes
from .california_calculator import CaliforniaCalculator, calculate_california_taxes, calculate_all_taxes

__all__ = [
    'load_tax_tables',
    'calculate_tax_by_bracket',
    'get_standard_deduction',
    'get_tax_brackets',
    'FederalCalculator',
    'calculate_federal_taxes',
    'CaliforniaCalculator',
    'calculate_california_taxes',
    'calculate_all_taxes',
]
