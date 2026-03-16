"""Data models for tax return application."""
from .w2 import W2
from .form1099 import (
    Form1099Base,
    Form1099NEC,
    Form1099INT,
    Form1099DIV,
    create_1099_form,
)
from .tax_return import (
    TaxReturn,
    PersonalInfo,
    FilingStatus,
)

__all__ = [
    'W2',
    'Form1099Base',
    'Form1099NEC',
    'Form1099INT',
    'Form1099DIV',
    'create_1099_form',
    'TaxReturn',
    'PersonalInfo',
    'FilingStatus',
]
