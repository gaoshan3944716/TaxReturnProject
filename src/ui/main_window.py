"""Main application window for the tax return application."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import json
from typing import Optional
from ..models.tax_return import TaxReturn, PersonalInfo, FilingStatus, W2
from ..models.form1099 import Form1099NEC, Form1099INT, Form1099DIV
from ..tax_calculator import calculate_all_taxes
from ..pdf_generator import generate_form1040_pdf, generate_ca540_pdf, generate_summary_report


class TaxReturnApp:
    """Main application window for tax return preparation."""

    def __init__(self, root: tk.Tk):
        """
        Initialize the tax return application.

        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("California Tax Return Assistant")
        self.root.geometry("1000x700")

        # Current tax return
        self.tax_return: Optional[TaxReturn] = None
        self.current_file: Optional[str] = None

        # Create UI
        self._create_menu()
        self._create_main_layout()

        # Create new tax return by default
        self._new_tax_return()

    def _create_menu(self) -> None:
        """Create application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Tax Return", command=self._new_tax_return)
        file_menu.add_command(label="Open...", command=self._open_tax_return)
        file_menu.add_command(label="Save", command=self._save_tax_return)
        file_menu.add_command(label="Save As...", command=self._save_tax_return_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)

    def _create_main_layout(self) -> None:
        """Create main application layout."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Personal Info tab
        self._create_personal_info_tab()

        # Income tab
        self._create_income_tab()

        # Deductions tab
        self._create_deductions_tab()

        # Results tab
        self._create_results_tab()

        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _create_personal_info_tab(self) -> None:
        """Create personal information tab."""
        self.personal_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.personal_frame, text="Personal Info")

        # Form frame
        form_frame = ttk.LabelFrame(self.personal_frame, text="Tax Year", padding=10)
        form_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(form_frame, text="Tax Year:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.tax_year_var = tk.StringVar(value="2025")
        ttk.Entry(form_frame, textvariable=self.tax_year_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5)

        # Filing status
        status_frame = ttk.LabelFrame(self.personal_frame, text="Filing Status", padding=10)
        status_frame.pack(fill=tk.X, padx=10, pady=5)

        self.filing_status_var = tk.StringVar(value="single")
        ttk.Radiobutton(status_frame, text="Single", variable=self.filing_status_var,
                       value="single").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Radiobutton(status_frame, text="Married Filing Jointly", variable=self.filing_status_var,
                       value="married_filing_jointly").grid(row=0, column=1, sticky=tk.W, padx=20, pady=2)
        ttk.Radiobutton(status_frame, text="Married Filing Separately", variable=self.filing_status_var,
                       value="married_filing_separately").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Radiobutton(status_frame, text="Head of Household", variable=self.filing_status_var,
                       value="head_of_household").grid(row=1, column=1, sticky=tk.W, padx=20, pady=2)

        # Personal details
        personal_frame = ttk.LabelFrame(self.personal_frame, text="Personal Details", padding=10)
        personal_frame.pack(fill=tk.X, padx=10, pady=5)

        # Name
        ttk.Label(personal_frame, text="First Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.first_name_var = tk.StringVar()
        ttk.Entry(personal_frame, textvariable=self.first_name_var, width=30).grid(row=0, column=1, sticky=tk.W, padx=5)

        ttk.Label(personal_frame, text="Middle Initial:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=10)
        self.middle_initial_var = tk.StringVar()
        ttk.Entry(personal_frame, textvariable=self.middle_initial_var, width=5).grid(row=0, column=3, sticky=tk.W, padx=5)

        ttk.Label(personal_frame, text="Last Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.last_name_var = tk.StringVar()
        ttk.Entry(personal_frame, textvariable=self.last_name_var, width=30).grid(row=1, column=1, sticky=tk.W, padx=5)

        # SSN
        ttk.Label(personal_frame, text="SSN:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.ssn_var = tk.StringVar()
        ttk.Entry(personal_frame, textvariable=self.ssn_var, width=15).grid(row=2, column=1, sticky=tk.W, padx=5)

        # Address
        ttk.Label(personal_frame, text="Street Address:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.street_address_var = tk.StringVar()
        ttk.Entry(personal_frame, textvariable=self.street_address_var, width=50).grid(row=3, column=1, columnspan=3, sticky=tk.W, padx=5)

        ttk.Label(personal_frame, text="City:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.city_var = tk.StringVar()
        ttk.Entry(personal_frame, textvariable=self.city_var, width=20).grid(row=4, column=1, sticky=tk.W, padx=5)

        ttk.Label(personal_frame, text="State:").grid(row=4, column=2, sticky=tk.W, pady=5, padx=10)
        self.state_var = tk.StringVar(value="CA")
        ttk.Entry(personal_frame, textvariable=self.state_var, width=5).grid(row=4, column=3, sticky=tk.W, padx=5)

        ttk.Label(personal_frame, text="ZIP:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.zip_var = tk.StringVar()
        ttk.Entry(personal_frame, textvariable=self.zip_var, width=15).grid(row=5, column=1, sticky=tk.W, padx=5)

    def _create_income_tab(self) -> None:
        """Create income tab."""
        self.income_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.income_frame, text="Income")

        # W-2 section
        w2_frame = ttk.LabelFrame(self.income_frame, text="W-2 Forms", padding=10)
        w2_frame.pack(fill=tk.X, padx=10, pady=5)

        w2_button_frame = ttk.Frame(w2_frame)
        w2_button_frame.pack(fill=tk.X)
        ttk.Button(w2_button_frame, text="Import W-2 PDF", command=self._import_w2).pack(side=tk.LEFT, pady=5)
        ttk.Button(w2_button_frame, text="Add W-2 Manually", command=self._add_w2_manual).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(w2_button_frame, text="Remove Selected", command=self._remove_w2).pack(side=tk.LEFT, padx=5, pady=5)

        # W-2 list
        columns = ('employer', 'wages', 'fed_tax')
        self.w2_tree = ttk.Treeview(w2_frame, columns=columns, show='headings', height=6)
        self.w2_tree.heading('employer', text='Employer')
        self.w2_tree.heading('wages', text='Wages')
        self.w2_tree.heading('fed_tax', text='Fed Tax')
        self.w2_tree.column('employer', width=200)
        self.w2_tree.column('wages', width=100)
        self.w2_tree.column('fed_tax', width=100)
        self.w2_tree.pack(fill=tk.BOTH, expand=True, pady=5)

        # 1099 section
        form1099_frame = ttk.LabelFrame(self.income_frame, text="1099 Forms", padding=10)
        form1099_frame.pack(fill=tk.X, padx=10, pady=5)

        form1099_button_frame = ttk.Frame(form1099_frame)
        form1099_button_frame.pack(fill=tk.X)
        ttk.Button(form1099_button_frame, text="Import 1099 PDF", command=self._import_1099).pack(side=tk.LEFT, pady=5)
        ttk.Button(form1099_button_frame, text="Add 1099 Manually", command=self._add_1099_manual).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(form1099_button_frame, text="Remove Selected", command=self._remove_1099).pack(side=tk.LEFT, padx=5, pady=5)

        # 1099 list
        columns1099 = ('type', 'payer', 'amount')
        self.form1099_tree = ttk.Treeview(form1099_frame, columns=columns1099, show='headings', height=6)
        self.form1099_tree.heading('type', text='Form Type')
        self.form1099_tree.heading('payer', text='Payer')
        self.form1099_tree.heading('amount', text='Amount')
        self.form1099_tree.column('type', width=100)
        self.form1099_tree.column('payer', width=200)
        self.form1099_tree.column('amount', width=100)
        self.form1099_tree.pack(fill=tk.BOTH, expand=True, pady=5)

    def _create_deductions_tab(self) -> None:
        """Create deductions tab."""
        self.deductions_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.deductions_frame, text="Deductions")

        # Deduction type
        ded_type_frame = ttk.LabelFrame(self.deductions_frame, text="Deduction Type", padding=10)
        ded_type_frame.pack(fill=tk.X, padx=10, pady=5)

        self.deduction_type_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(ded_type_frame, text="Use Standard Deduction", variable=self.deduction_type_var,
                       command=self._update_deduction_ui).pack(anchor=tk.W)

        # Standard deduction info
        self.std_ded_label = ttk.Label(ded_type_frame, text="Standard Deduction: $14,600 (Single)")
        self.std_ded_label.pack(anchor=tk.W, pady=5)

        # Itemized deductions (hidden by default)
        self.itemized_frame = ttk.LabelFrame(self.deductions_frame, text="Itemized Deductions", padding=10)
        self.itemized_ded_var = tk.StringVar(value="0.00")
        ttk.Label(self.itemized_frame, text="Total Itemized Deductions:").pack(side=tk.LEFT, pady=5)
        ttk.Entry(self.itemized_frame, textvariable=self.itemized_ded_var, width=20).pack(side=tk.LEFT, padx=5)

        # Adjustments
        adj_frame = ttk.LabelFrame(self.deductions_frame, text="Income Adjustments", padding=10)
        adj_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(adj_frame, text="Traditional IRA Contributions:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.ira_var = tk.StringVar(value="0.00")
        ttk.Entry(adj_frame, textvariable=self.ira_var, width=15).grid(row=0, column=1, sticky=tk.W, padx=5)

        ttk.Label(adj_frame, text="Student Loan Interest:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.student_loan_var = tk.StringVar(value="0.00")
        ttk.Entry(adj_frame, textvariable=self.student_loan_var, width=15).grid(row=1, column=1, sticky=tk.W, padx=5)

        ttk.Label(adj_frame, text="HSA Contributions:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.hsa_var = tk.StringVar(value="0.00")
        ttk.Entry(adj_frame, textvariable=self.hsa_var, width=15).grid(row=2, column=1, sticky=tk.W, padx=5)

        ttk.Label(adj_frame, text="Other Adjustments:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.other_adj_var = tk.StringVar(value="0.00")
        ttk.Entry(adj_frame, textvariable=self.other_adj_var, width=15).grid(row=3, column=1, sticky=tk.W, padx=5)

    def _create_results_tab(self) -> None:
        """Create results tab."""
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="Results")

        # Calculate button
        button_frame = ttk.Frame(self.results_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="Calculate Taxes", command=self._calculate_taxes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Generate PDF Forms", command=self._generate_pdfs).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Generate Summary", command=self._generate_summary).pack(side=tk.LEFT, padx=5)

        # Results display
        results_container = ttk.Frame(self.results_frame)
        results_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Federal results
        fed_frame = ttk.LabelFrame(results_container, text="Federal Tax (Form 1040)", padding=10)
        fed_frame.pack(fill=tk.X, pady=5)

        self.fed_results_text = tk.Text(fed_frame, height=8, width=70)
        self.fed_results_text.pack(fill=tk.BOTH, expand=True)

        # California results
        ca_frame = ttk.LabelFrame(results_container, text="California State Tax (Form 540)", padding=10)
        ca_frame.pack(fill=tk.X, pady=5)

        self.ca_results_text = tk.Text(ca_frame, height=8, width=70)
        self.ca_results_text.pack(fill=tk.BOTH, expand=True)

    def _new_tax_return(self) -> None:
        """Create a new tax return."""
        self.tax_return = TaxReturn()
        self.current_file = None
        self._clear_ui()

    def _open_tax_return(self) -> None:
        """Open a saved tax return."""
        file_path = filedialog.askopenfilename(
            title="Open Tax Return",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                self.tax_return = TaxReturn.from_dict(data)
                self.current_file = file_path
                self._load_from_tax_return()
                self.status_bar.config(text=f"Loaded: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {e}")

    def _save_tax_return(self) -> None:
        """Save the current tax return."""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self._save_tax_return_as()

    def _save_tax_return_as(self) -> None:
        """Save the tax return to a new file."""
        file_path = filedialog.asksaveasfilename(
            title="Save Tax Return",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self._save_to_file(file_path)

    def _save_to_file(self, file_path: str) -> None:
        """Save tax return to specified file."""
        try:
            self._sync_to_tax_return()
            data = self.tax_return.to_dict()
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            self.current_file = file_path
            self.status_bar.config(text=f"Saved: {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")

    def _clear_ui(self) -> None:
        """Clear all UI fields."""
        self.first_name_var.set("")
        self.last_name_var.set("")
        self.middle_initial_var.set("")
        self.ssn_var.set("")
        self.street_address_var.set("")
        self.city_var.set("")
        self.state_var.set("CA")
        self.zip_var.set("")
        self.tax_year_var.set("2025")
        self.filing_status_var.set("single")

        # Clear W-2 tree
        for item in self.w2_tree.get_children():
            self.w2_tree.delete(item)

        # Clear 1099 tree
        for item in self.form1099_tree.get_children():
            self.form1099_tree.delete(item)

        # Clear deduction fields
        self.deduction_type_var.set(True)
        self.itemized_ded_var.set("0.00")
        self.ira_var.set("0.00")
        self.student_loan_var.set("0.00")
        self.hsa_var.set("0.00")
        self.other_adj_var.set("0.00")

        # Clear results
        self.fed_results_text.delete(1.0, tk.END)
        self.ca_results_text.delete(1.0, tk.END)

    def _load_from_tax_return(self) -> None:
        """Load UI from tax return data."""
        info = self.tax_return.personal_info
        self.first_name_var.set(info.first_name)
        self.middle_initial_var.set(info.middle_initial)
        self.last_name_var.set(info.last_name)
        self.ssn_var.set(info.ssn)
        self.street_address_var.set(info.street_address)
        self.city_var.set(info.city)
        self.state_var.set(info.state)
        self.zip_var.set(info.zip_code)
        self.tax_year_var.set(str(self.tax_return.tax_year))
        self.filing_status_var.set(self.tax_return.filing_status.value)

        # Load W-2s
        for item in self.w2_tree.get_children():
            self.w2_tree.delete(item)
        for w2 in self.tax_return.w2_forms:
            self.w2_tree.insert('', 'end', values=(
                w2.employer_name,
                f"${w2.box1_wages:,.2f}",
                f"${w2.box2_federal_tax:,.2f}"
            ))

        # Load 1099s
        for item in self.form1099_tree.get_children():
            self.form1099_tree.delete(item)
        for form1099 in self.tax_return.form1099s:
            form_type = form1099.__class__.__name__.replace('Form', '')
            self.form1099_tree.insert('', 'end', values=(
                form_type,
                form1099.payer_name,
                f"${form1099.get_total_income():,.2f}"
            ))

        # Load deductions
        self.deduction_type_var.set(self.tax_return.use_standard_deduction)
        self.itemized_ded_var.set(str(self.tax_return.itemized_deductions))
        self.ira_var.set(str(self.tax_return.traditional_ira_contributions))
        self.student_loan_var.set(str(self.tax_return.student_loan_interest))
        self.hsa_var.set(str(self.tax_return.hsa_contributions))
        self.other_adj_var.set(str(self.tax_return.other_adjustments))

        self._update_deduction_ui()

    def _sync_to_tax_return(self) -> None:
        """Sync UI values to tax return object."""
        info = self.tax_return.personal_info
        info.first_name = self.first_name_var.get()
        info.middle_initial = self.middle_initial_var.get()
        info.last_name = self.last_name_var.get()
        info.ssn = self.ssn_var.get()
        info.street_address = self.street_address_var.get()
        info.city = self.city_var.get()
        info.state = self.state_var.get()
        info.zip_code = self.zip_var.get()

        self.tax_return.tax_year = int(self.tax_year_var.get())
        self.tax_return.filing_status = FilingStatus(self.filing_status_var.get())
        self.tax_return.use_standard_deduction = self.deduction_type_var.get()
        self.tax_return.itemized_deductions = float(self.itemized_ded_var.get())
        self.tax_return.traditional_ira_contributions = float(self.ira_var.get())
        self.tax_return.student_loan_interest = float(self.student_loan_var.get())
        self.tax_return.hsa_contributions = float(self.hsa_var.get())
        self.tax_return.other_adjustments = float(self.other_adj_var.get())

    def _update_deduction_ui(self) -> None:
        """Update deduction UI based on selected type."""
        if self.deduction_type_var.get():
            # Standard deduction
            self.itemized_frame.pack_forget()
            filing_status = self.filing_status_var.get()
            std_ded = {'single': 14600, 'married_filing_jointly': 29200,
                      'married_filing_separately': 14600, 'head_of_household': 21900}
            amount = std_ded.get(filing_status, 0)
            self.std_ded_label.config(text=f"Standard Deduction: ${amount:,.2f} ({filing_status.replace('_', ' ').title()})")
        else:
            # Itemized
            self.std_ded_label.config(text="")
            self.itemized_frame.pack(fill=tk.X, padx=10, pady=5)

    def _import_w2(self) -> None:
        """Import W-2 from PDF file."""
        file_path = filedialog.askopenfilename(
            title="Select W-2 PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_path:
            try:
                from ..pdf_parser import parse_w2_pdf
                w2 = parse_w2_pdf(file_path)
                if w2:
                    self.tax_return.add_w2(w2)
                    self.w2_tree.insert('', 'end', values=(
                        w2.employer_name or "Unknown Employer",
                        f"${w2.box1_wages:,.2f}",
                        f"${w2.box2_federal_tax:,.2f}"
                    ))
                    self.status_bar.config(text=f"Imported W-2 from {Path(file_path).name}")
                else:
                    messagebox.showwarning("Warning", "Could not parse W-2 PDF. Please enter manually.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import W-2: {e}")

    def _add_w2_manual(self) -> None:
        """Add W-2 manually."""
        # For simplicity, add a sample W-2
        w2 = W2(
            employer_name="Manual Entry",
            box1_wages=0.0,
            box2_federal_tax=0.0
        )
        self.tax_return.add_w2(w2)
        self.w2_tree.insert('', 'end', values=(
            w2.employer_name,
            f"${w2.box1_wages:,.2f}",
            f"${w2.box2_federal_tax:,.2f}"
        ))

    def _remove_w2(self) -> None:
        """Remove selected W-2."""
        selected = self.w2_tree.selection()
        if selected:
            index = self.w2_tree.index(selected[0])
            if 0 <= index < len(self.tax_return.w2_forms):
                del self.tax_return.w2_forms[index]
            self.w2_tree.delete(selected)

    def _import_1099(self) -> None:
        """Import 1099 from PDF file."""
        file_path = filedialog.askopenfilename(
            title="Select 1099 PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_path:
            try:
                from ..pdf_parser import parse_1099_pdf
                form1099 = parse_1099_pdf(file_path)
                if form1099:
                    self.tax_return.add_1099(form1099)
                    form_type = form1099.__class__.__name__.replace('Form', '')
                    self.form1099_tree.insert('', 'end', values=(
                        form_type,
                        form1099.payer_name or "Unknown Payer",
                        f"${form1099.get_total_income():,.2f}"
                    ))
                    self.status_bar.config(text=f"Imported 1099 from {Path(file_path).name}")
                else:
                    messagebox.showwarning("Warning", "Could not parse 1099 PDF. Please enter manually.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import 1099: {e}")

    def _add_1099_manual(self) -> None:
        """Add 1099 manually."""
        # For simplicity, add a sample 1099-NEC
        form1099 = Form1099NEC(
            payer_name="Manual Entry",
            box1_nonemployee_compensation=0.0
        )
        self.tax_return.add_1099(form1099)
        self.form1099_tree.insert('', 'end', values=(
            "1099-NEC",
            form1099.payer_name,
            f"${form1099.get_total_income():,.2f}"
        ))

    def _remove_1099(self) -> None:
        """Remove selected 1099."""
        selected = self.form1099_tree.selection()
        if selected:
            index = self.form1099_tree.index(selected[0])
            if 0 <= index < len(self.tax_return.form1099s):
                del self.tax_return.form1099s[index]
            self.form1099_tree.delete(selected)

    def _calculate_taxes(self) -> None:
        """Calculate federal and California taxes."""
        self._sync_to_tax_return()
        try:
            calculate_all_taxes(self.tax_return, self.tax_return.tax_year)
            self._display_results()
            self.status_bar.config(text="Tax calculation complete")
        except Exception as e:
            messagebox.showerror("Error", f"Calculation failed: {e}")

    def _display_results(self) -> None:
        """Display calculation results."""
        # Federal results
        fed_text = f"""Gross Income: ${self.tax_return.federal_gross_income:,.2f}
Total Income: ${self.tax_return.federal_total_income:,.2f}
Adjusted Gross Income: ${self.tax_return.federal_agi:,.2f}
Taxable Income: ${self.tax_return.federal_taxable_income:,.2f}
Tax: ${self.tax_return.federal_tax:,.2f}
Tax Withheld: ${self.tax_return.federal_tax_withheld:,.2f}

"""
        if self.tax_return.federal_refund_or_owed > 0:
            fed_text += f"REFUND: ${self.tax_return.federal_refund_or_owed:,.2f}"
        else:
            fed_text += f"AMOUNT OWED: ${abs(self.tax_return.federal_refund_or_owed):,.2f}"

        self.fed_results_text.delete(1.0, tk.END)
        self.fed_results_text.insert(tk.END, fed_text)

        # California results
        ca_text = f"""Federal AGI: ${self.tax_return.federal_agi:,.2f}
CA AGI: ${self.tax_return.ca_agi:,.2f}
Taxable Income: ${self.tax_return.ca_taxable_income:,.2f}
Tax: ${self.tax_return.ca_tax:,.2f}
Tax Withheld: ${self.tax_return.ca_tax_withheld:,.2f}
SDI Withheld: ${self.tax_return.ca_sdi_withheld:,.2f}
Total Withheld: ${self.tax_return.ca_tax_withheld + self.tax_return.ca_sdi_withheld:,.2f}

"""
        if self.tax_return.ca_refund_or_owed > 0:
            ca_text += f"REFUND: ${self.tax_return.ca_refund_or_owed:,.2f}"
        else:
            ca_text += f"AMOUNT OWED: ${abs(self.tax_return.ca_refund_or_owed):,.2f}"

        self.ca_results_text.delete(1.0, tk.END)
        self.ca_results_text.insert(tk.END, ca_text)

    def _generate_pdfs(self) -> None:
        """Generate PDF forms."""
        if self.tax_return.federal_agi == 0:
            messagebox.showwarning("Warning", "Please calculate taxes first.")
            return

        try:
            base_path = filedialog.asksaveasfilename(
                title="Save PDF Forms",
                defaultextension="",
                filetypes=[("All files", "*.*")]
            )
            if base_path:
                base_path = Path(base_path)
                form1040_path = base_path.parent / f"{base_path.stem}_Form1040.pdf"
                ca540_path = base_path.parent / f"{base_path.stem}_Form540.pdf"

                generate_form1040_pdf(self.tax_return, str(form1040_path))
                generate_ca540_pdf(self.tax_return, str(ca540_path))

                self.status_bar.config(text=f"Generated PDFs: {form1040_path.name}, {ca540_path.name}")
                messagebox.showinfo("Success", f"PDF forms saved:\n{form1040_path}\n{ca540_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDFs: {e}")

    def _generate_summary(self) -> None:
        """Generate summary report."""
        if self.tax_return.federal_agi == 0:
            messagebox.showwarning("Warning", "Please calculate taxes first.")
            return

        try:
            file_path = filedialog.asksaveasfilename(
                title="Save Summary Report",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("HTML files", "*.html"), ("All files", "*.*")]
            )
            if file_path:
                format_type = 'html' if file_path.lower().endswith('.html') else 'text'
                generate_summary_report(self.tax_return, file_path, format_type)
                self.status_bar.config(text=f"Generated summary: {Path(file_path).name}")
                messagebox.showinfo("Success", f"Summary saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate summary: {e}")

    def _show_about(self) -> None:
        """Show about dialog."""
        about_text = """California Tax Return Assistant

A desktop application for preparing federal (Form 1040)
and California state (Form 540) tax returns.

Features:
- Import W-2 and 1099 PDF forms
- Calculate federal and California taxes
- Generate PDF forms and summary reports

DISCLAIMER: This application is for informational
purposes only. For official tax filing, please use
IRS-approved software or consult a tax professional.
"""
        messagebox.showinfo("About", about_text)


def main() -> None:
    """Run the tax return application."""
    root = tk.Tk()
    app = TaxReturnApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
