"""Data models for various 1099 forms."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class Form1099Base(ABC):
    """Base class for all 1099 forms."""

    # Payer Information
    payer_ein: str = ""
    payer_name: str = ""
    payer_address: str = ""
    payer_city_state_zip: str = ""

    # Recipient Information
    recipient_tin: str = ""
    recipient_name: str = ""
    recipient_address: str = ""
    recipient_city_state_zip: str = ""

    @abstractmethod
    def get_total_income(self) -> float:
        """Get total income amount for tax calculation."""
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """Convert form to dictionary."""
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict):
        """Create form from dictionary."""
        pass


@dataclass
class Form1099NEC(Form1099Base):
    """Form 1099-NEC: Nonemployee Compensation."""

    # Box 1: Nonemployee compensation
    box1_nonemployee_compensation: float = 0.0

    # Box 4: Federal income tax withheld
    box4_federal_tax_withheld: float = 0.0

    # State information
    state_code: str = ""
    state_income: float = 0.0
    state_tax_withheld: float = 0.0

    def get_total_income(self) -> float:
        """Get total income from this 1099-NEC."""
        return self.box1_nonemployee_compensation

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'payer_ein': self.payer_ein,
            'payer_name': self.payer_name,
            'payer_address': self.payer_address,
            'payer_city_state_zip': self.payer_city_state_zip,
            'recipient_tin': self.recipient_tin,
            'recipient_name': self.recipient_name,
            'recipient_address': self.recipient_address,
            'recipient_city_state_zip': self.recipient_city_state_zip,
            'box1_nonemployee_compensation': self.box1_nonemployee_compensation,
            'box4_federal_tax_withheld': self.box4_federal_tax_withheld,
            'state_code': self.state_code,
            'state_income': self.state_income,
            'state_tax_withheld': self.state_tax_withheld,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Form1099NEC':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class Form1099INT(Form1099Base):
    """Form 1099-INT: Interest Income."""

    # Box 1: Interest income
    box1_interest_income: float = 0.0

    # Box 2: Early withdrawal penalty
    box2_early_withdrawal_penalty: float = 0.0

    # Box 3: Interest on U.S. Treasury obligations
    box3_treasury_interest: float = 0.0

    # Box 4: Federal income tax withheld
    box4_federal_tax_withheld: float = 0.0

    # Box 5: Investment expenses
    box5_investment_expenses: float = 0.0

    # Box 6: Foreign tax paid
    box6_foreign_tax_paid: float = 0.0

    # Box 7: Foreign country or U.S. possession
    box7_foreign_country: str = ""

    # Box 8: Tax-exempt interest
    box8_tax_exempt_interest: float = 0.0

    # State information
    state_code: str = ""
    state_identification: str = ""
    state_tax_withheld: float = 0.0

    def get_total_income(self) -> float:
        """Get total income from this 1099-INT."""
        return self.box1_interest_income

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'payer_ein': self.payer_ein,
            'payer_name': self.payer_name,
            'payer_address': self.payer_address,
            'payer_city_state_zip': self.payer_city_state_zip,
            'recipient_tin': self.recipient_tin,
            'recipient_name': self.recipient_name,
            'recipient_address': self.recipient_address,
            'recipient_city_state_zip': self.recipient_city_state_zip,
            'box1_interest_income': self.box1_interest_income,
            'box2_early_withdrawal_penalty': self.box2_early_withdrawal_penalty,
            'box3_treasury_interest': self.box3_treasury_interest,
            'box4_federal_tax_withheld': self.box4_federal_tax_withheld,
            'box5_investment_expenses': self.box5_investment_expenses,
            'box6_foreign_tax_paid': self.box6_foreign_tax_paid,
            'box7_foreign_country': self.box7_foreign_country,
            'box8_tax_exempt_interest': self.box8_tax_exempt_interest,
            'state_code': self.state_code,
            'state_identification': self.state_identification,
            'state_tax_withheld': self.state_tax_withheld,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Form1099INT':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class Form1099DIV(Form1099Base):
    """Form 1099-DIV: Dividends and Distributions."""

    # Box 1a: Total ordinary dividends
    box1a_total_ordinary_dividends: float = 0.0

    # Box 1b: Qualified dividends
    box1b_qualified_dividends: float = 0.0

    # Box 2a: Total capital gain distributions
    box2a_total_capital_gain: float = 0.0

    # Box 2b: Unrecaptured Section 1250 gain
    box2b_unrecaptured_section1250: float = 0.0

    # Box 2c: Section 1202 gain
    box2c_section1202_gain: float = 0.0

    # Box 2d: Collectibles gain
    box2d_collectibles_gain: float = 0.0

    # Box 3: Nondividend distributions
    box3_nondividend_distributions: float = 0.0

    # Box 4: Federal income tax withheld
    box4_federal_tax_withheld: float = 0.0

    # Box 5: Section 199A dividends
    box5_section199a_dividends: float = 0.0

    # Box 6: Investment expenses
    box6_investment_expenses: float = 0.0

    # Box 7: Foreign tax paid
    box7_foreign_tax_paid: float = 0.0

    # Box 8: Foreign country or U.S. possession
    box8_foreign_country: str = ""

    # State information
    state_code: str = ""
    state_identification: str = ""
    state_tax_withheld: float = 0.0

    def get_total_income(self) -> float:
        """Get total income from this 1099-DIV."""
        return self.box1a_total_ordinary_dividends

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'payer_ein': self.payer_ein,
            'payer_name': self.payer_name,
            'payer_address': self.payer_address,
            'payer_city_state_zip': self.payer_city_state_zip,
            'recipient_tin': self.recipient_tin,
            'recipient_name': self.recipient_name,
            'recipient_address': self.recipient_address,
            'recipient_city_state_zip': self.recipient_city_state_zip,
            'box1a_total_ordinary_dividends': self.box1a_total_ordinary_dividends,
            'box1b_qualified_dividends': self.box1b_qualified_dividends,
            'box2a_total_capital_gain': self.box2a_total_capital_gain,
            'box2b_unrecaptured_section1250': self.box2b_unrecaptured_section1250,
            'box2c_section1202_gain': self.box2c_section1202_gain,
            'box2d_collectibles_gain': self.box2d_collectibles_gain,
            'box3_nondividend_distributions': self.box3_nondividend_distributions,
            'box4_federal_tax_withheld': self.box4_federal_tax_withheld,
            'box5_section199a_dividends': self.box5_section199a_dividends,
            'box6_investment_expenses': self.box6_investment_expenses,
            'box7_foreign_tax_paid': self.box7_foreign_tax_paid,
            'box8_foreign_country': self.box8_foreign_country,
            'state_code': self.state_code,
            'state_identification': self.state_identification,
            'state_tax_withheld': self.state_tax_withheld,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Form1099DIV':
        """Create from dictionary."""
        return cls(**data)


def create_1099_form(form_type: str) -> Optional[Form1099Base]:
    """Factory function to create 1099 form by type."""
    form_classes = {
        '1099-NEC': Form1099NEC,
        '1099-INT': Form1099INT,
        '1099-DIV': Form1099DIV,
    }
    return form_classes.get(form_type)
