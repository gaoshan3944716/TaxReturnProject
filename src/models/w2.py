"""Data model for W-2 Wage and Tax Statement."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class W2:
    """W-2 Wage and Tax Statement data model."""

    # Employer Information
    employer_ein: str = ""
    employer_name: str = ""
    employer_address: str = ""
    employer_city_state_zip: str = ""

    # Employee Information
    employee_ssn: str = ""
    employee_name: str = ""
    employee_address: str = ""
    employee_city_state_zip: str = ""

    # Box 1: Wages, tips, other compensation
    box1_wages: float = 0.0

    # Box 2: Federal income tax withheld
    box2_federal_tax: float = 0.0

    # Box 3: Social security wages
    box3_ss_wages: float = 0.0

    # Box 4: Social security tax withheld
    box4_ss_tax: float = 0.0

    # Box 5: Medicare wages and tips
    box5_medicare_wages: float = 0.0

    # Box 6: Medicare tax withheld
    box6_medicare_tax: float = 0.0

    # Box 7: Social security tips
    box7_ss_tips: float = 0.0

    # Box 8: Allocated tips
    box8_allocated_tips: float = 0.0

    # Box 10: Dependent care benefits
    box10_dependent_care: float = 0.0

    # Box 11: Nonqualified plans
    box11_nonqualified_plans: float = 0.0

    # Box 12a-d: Various codes and amounts (simplified)
    box12_codes: list = None

    # Box 13: Statutory employee, Retirement plan, Third-party sick pay
    box13_statutory_employee: bool = False
    box13_retirement_plan: bool = False
    box13_third_party_sick_pay: bool = False

    # Box 14: Other
    box14_other: str = ""

    # Box 15a: Employer's state ID number
    box15_state_id: str = ""

    # Box 16: State wages, tips, etc.
    box16_state_wages: float = 0.0

    # Box 17: State income tax
    box17_state_tax: float = 0.0

    # Box 18: Local wages, tips, etc.
    box18_local_wages: float = 0.0

    # Box 19: Local income tax
    box19_local_tax: float = 0.0

    # Box 20: Locality name
    box20_locality: str = ""

    # State code (CA for California)
    state_code: str = ""

    def __post_init__(self):
        if self.box12_codes is None:
            self.box12_codes = []

    def to_dict(self) -> dict:
        """Convert W2 to dictionary."""
        return {
            'employer_ein': self.employer_ein,
            'employer_name': self.employer_name,
            'employer_address': self.employer_address,
            'employer_city_state_zip': self.employer_city_state_zip,
            'employee_ssn': self.employee_ssn,
            'employee_name': self.employee_name,
            'employee_address': self.employee_address,
            'employee_city_state_zip': self.employee_city_state_zip,
            'box1_wages': self.box1_wages,
            'box2_federal_tax': self.box2_federal_tax,
            'box3_ss_wages': self.box3_ss_wages,
            'box4_ss_tax': self.box4_ss_tax,
            'box5_medicare_wages': self.box5_medicare_wages,
            'box6_medicare_tax': self.box6_medicare_tax,
            'box7_ss_tips': self.box7_ss_tips,
            'box8_allocated_tips': self.box8_allocated_tips,
            'box10_dependent_care': self.box10_dependent_care,
            'box11_nonqualified_plans': self.box11_nonqualified_plans,
            'box12_codes': self.box12_codes,
            'box13_statutory_employee': self.box13_statutory_employee,
            'box13_retirement_plan': self.box13_retirement_plan,
            'box13_third_party_sick_pay': self.box13_third_party_sick_pay,
            'box14_other': self.box14_other,
            'box15_state_id': self.box15_state_id,
            'box16_state_wages': self.box16_state_wages,
            'box17_state_tax': self.box17_state_tax,
            'box18_local_wages': self.box18_local_wages,
            'box19_local_tax': self.box19_local_tax,
            'box20_locality': self.box20_locality,
            'state_code': self.state_code,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'W2':
        """Create W2 from dictionary."""
        return cls(**data)

    def validate(self) -> list[str]:
        """Validate W2 data and return list of errors."""
        errors = []

        # Validate SSN format (XXX-XX-XXXX)
        if self.employee_ssn and len(self.employee_ssn.replace('-', '')) != 9:
            errors.append("Employee SSN must be 9 digits")

        # Validate EIN format (XX-XXXXXXX)
        if self.employer_ein and len(self.employer_ein.replace('-', '')) != 9:
            errors.append("Employer EIN must be 9 digits")

        # Validate state code
        if self.state_code and len(self.state_code) != 2:
            errors.append("State code must be 2 letters")

        return errors
