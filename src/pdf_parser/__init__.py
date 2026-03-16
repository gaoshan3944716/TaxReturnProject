"""PDF parser module for tax forms."""
from .base_parser import BasePDFParser
from .w2_parser import W2Parser, parse_w2_pdf
from .form1099_parser import Form1099Parser, parse_1099_pdf

__all__ = [
    'BasePDFParser',
    'W2Parser',
    'parse_w2_pdf',
    'Form1099Parser',
    'parse_1099_pdf',
]
