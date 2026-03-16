"""Data model for complete tax return."""
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

from .w2 import W2
from .form1099 import Form1099Base, Form1099NEC, Form1099INT, Form1099DIV


class FilingStatus(Enum):
    """Tax filing status options."""
    SINGLE = "single"
    MARRIED_FILING_JOINTLY = "married_filing_jointly"
    MARRIED_FILING_SEPARATELY = "married_filing_separately"
    HEAD_OF_HOUSEHOLD = "head_of_household"


@dataclass
class PersonalInfo:
    """Personal information for tax return."""

    first_name: str = ""
    last_name: str = ""
    middle_initial: str = ""
    ssn: str = ""
    date_of_birth: str = ""
    occupation: str = ""

    # Address
    street_address: str = ""
    apartment: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    country: str = "USA"

    # Spouse information (if married filing jointly)
    spouse_first_name: str = ""
    spouse_last_name: str = ""
    spouse_ssn: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'middle_initial': self.middle_initial,
            'ssn': self.ssn,
            'date_of_birth': self.date_of_birth,
            'occupation': self.occupation,
            'street_address': self.street_address,
            'apartment': self.apartment,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'country': self.country,
            'spouse_first_name': self.spouse_first_name,
            'spouse_last_name': self.spouse_last_name,
            'spouse_ssn': self.spouse_ssn,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PersonalInfo':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class TaxReturn:
    """Complete tax return data."""

    tax_year: int = 2025

    # Personal information
    personal_info: PersonalInfo = field(default_factory=PersonalInfo)
    filing_status: FilingStatus = FilingStatus.SINGLE

    # Income sources
    w2_forms: list[W2] = field(default_factory=list)
    form1099s: list[Form1099Base] = field(default_factory=list)

    # Deductions
    use_standard_deduction: bool = True
    itemized_deductions: float = 0.0

    # Income adjustments
    traditional_ira_contributions: float = 0.0
    student_loan_interest: float = 0.0
    hsa_contributions: float = 0.0
    other_adjustments: float = 0.0

    # Federal tax results (calculated)
    federal_gross_income: float = 0.0
    federal_total_income: float = 0.0
    federal_agi: float = 0.0
    federal_taxable_income: float = 0.0
    federal_tax: float = 0.0
    federal_tax_withheld: float = 0.0
    federal_refund_or_owed: float = 0.0

    # California tax results (calculated)
    ca_gross_income: float = 0.0
    ca_agi: float = 0.0
    ca_taxable_income: float = 0.0
    ca_tax: float = 0.0
    ca_tax_withheld: float = 0.0
    ca_sdi_withheld: float = 0.0
    ca_refund_or_owed: float = 0.0

    def add_w2(self, w2: W2) -> None:
        """Add a W-2 form to the return."""
        self.w2_forms.append(w2)

    def add_1099(self, form1099: Form1099Base) -> None:
        """Add a 1099 form to the return."""
        self.form1099s.append(form1099)

    def get_total_wages(self) -> float:
        """Calculate total wages from all W-2 forms."""
        return sum(w2.box1_wages for w2 in self.w2_forms)

    def get_total_federal_tax_withheld_w2(self) -> float:
        """Calculate total federal tax withheld from W-2 forms."""
        return sum(w2.box2_federal_tax for w2 in self.w2_forms)

    def get_total_ca_tax_withheld_w2(self) -> float:
        """Calculate total CA tax withheld from W-2 forms."""
        return sum(w2.box17_state_tax for w2 in self.w2_forms if w2.state_code == 'CA')

    def get_total_ca_sdi_withheld_w2(self) -> float:
        """Calculate total CA SDI withheld from W-2 forms (box 14, code 'SDI')."""
        total = 0.0
        for w2 in self.w2_forms:
            if w2.state_code == 'CA' and w2.box14_other:
                # Parse box 14 for SDI withholding
                # Format: "SDI: 45.00" or similar
                for item in w2.box14_other.split(','):
                    item = item.strip().upper()
                    if 'SDI' in item:
                        try:
                            amount = float(item.split(':')[-1].strip().replace('$', ''))
                            total += amount
                        except (ValueError, IndexError):
                            continue
        return total

    def get_total_1099_income(self) -> float:
        """Calculate total income from all 1099 forms."""
        return sum(form1099.get_total_income() for form1099 in self.form1099s)

    def get_total_federal_tax_withheld_1099(self) -> float:
        """Calculate total federal tax withheld from 1099 forms."""
        total = 0.0
        for form1099 in self.form1099s:
            if isinstance(form1099, Form1099NEC):
                total += form1099.box4_federal_tax_withheld
            elif isinstance(form1099, Form1099INT):
                total += form1099.box4_federal_tax_withheld
            elif isinstance(form1099, Form1099DIV):
                total += form1099.box4_federal_tax_withheld
        return total

    def to_dict(self) -> dict:
        """Convert tax return to dictionary for saving."""
        return {
            'tax_year': self.tax_year,
            'personal_info': self.personal_info.to_dict(),
            'filing_status': self.filing_status.value,
            'w2_forms': [w2.to_dict() for w2 in self.w2_forms],
            'form1099s': self._serialize_1099s(),
            'use_standard_deduction': self.use_standard_deduction,
            'itemized_deductions': self.itemized_deductions,
            'traditional_ira_contributions': self.traditional_ira_contributions,
            'student_loan_interest': self.student_loan_interest,
            'hsa_contributions': self.hsa_contributions,
            'other_adjustments': self.other_adjustments,
            'federal_gross_income': self.federal_gross_income,
            'federal_total_income': self.federal_total_income,
            'federal_agi': self.federal_agi,
            'federal_taxable_income': self.federal_taxable_income,
            'federal_tax': self.federal_tax,
            'federal_tax_withheld': self.federal_tax_withheld,
            'federal_refund_or_owed': self.federal_refund_or_owed,
            'ca_gross_income': self.ca_gross_income,
            'ca_agi': self.ca_agi,
            'ca_taxable_income': self.ca_taxable_income,
            'ca_tax': self.ca_tax,
            'ca_tax_withheld': self.ca_tax_withheld,
            'ca_sdi_withheld': self.ca_sdi_withheld,
            'ca_refund_or_owed': self.ca_refund_or_owed,
        }

    def _serialize_1099s(self) -> list:
        """Serialize 1099 forms to dictionaries."""
        result = []
        for form1099 in self.form1099s:
            form_data = form1099.to_dict()
            form_data['form_type'] = form1099.__class__.__name__
            result.append(form_data)
        return result

    @classmethod
    def from_dict(cls, data: dict) -> 'TaxReturn':
        """Create tax return from dictionary."""
        tax_return = cls(
            tax_year=data.get('tax_year', 2025),
            personal_info=PersonalInfo.from_dict(data.get('personal_info', {})),
            filing_status=FilingStatus(data.get('filing_status', 'single')),
            use_standard_deduction=data.get('use_standard_deduction', True),
            itemized_deductions=data.get('itemized_deductions', 0.0),
            traditional_ira_contributions=data.get('traditional_ira_contributions', 0.0),
            student_loan_interest=data.get('student_loan_interest', 0.0),
            hsa_contributions=data.get('hsa_contributions', 0.0),
            other_adjustments=data.get('other_adjustments', 0.0),
            federal_gross_income=data.get('federal_gross_income', 0.0),
            federal_total_income=data.get('federal_total_income', 0.0),
            federal_agi=data.get('federal_agi', 0.0),
            federal_taxable_income=data.get('federal_taxable_income', 0.0),
            federal_tax=data.get('federal_tax', 0.0),
            federal_tax_withheld=data.get('federal_tax_withheld', 0.0),
            federal_refund_or_owed=data.get('federal_refund_or_owed', 0.0),
            ca_gross_income=data.get('ca_gross_income', 0.0),
            ca_agi=data.get('ca_agi', 0.0),
            ca_taxable_income=data.get('ca_taxable_income', 0.0),
            ca_tax=data.get('ca_tax', 0.0),
            ca_tax_withheld=data.get('ca_tax_withheld', 0.0),
            ca_sdi_withheld=data.get('ca_sdi_withheld', 0.0),
            ca_refund_or_owed=data.get('ca_refund_or_owed', 0.0),
        )

        # Restore W-2 forms
        for w2_data in data.get('w2_forms', []):
            tax_return.w2_forms.append(W2.from_dict(w2_data))

        # Restore 1099 forms
        from .form1099 import Form1099NEC, Form1099INT, Form1099DIV
        form_classes = {
            'Form1099NEC': Form1099NEC,
            'Form1099INT': Form1099INT,
            'Form1099DIV': Form1099DIV,
        }
        for form1099_data in data.get('form1099s', []):
            form_type = form1099_data.pop('form_type', None)
            if form_type and form_type in form_classes:
                tax_return.form1099s.append(form_classes[form_type].from_dict(form1099_data))

        return tax_return

    def clear_calculations(self) -> None:
        """Clear all calculated tax results."""
        self.federal_gross_income = 0.0
        self.federal_total_income = 0.0
        self.federal_agi = 0.0
        self.federal_taxable_income = 0.0
        self.federal_tax = 0.0
        self.federal_tax_withheld = 0.0
        self.federal_refund_or_owed = 0.0
        self.ca_gross_income = 0.0
        self.ca_agi = 0.0
        self.ca_taxable_income = 0.0
        self.ca_tax = 0.0
        self.ca_tax_withheld = 0.0
        self.ca_sdi_withheld = 0.0
        self.ca_refund_or_owed = 0.0
