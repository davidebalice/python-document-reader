import re
import pdfplumber
import logging

# Espressioni regolari per i campi
REGEX_BUSINESS_NAME = r"Business Name 01: (.*)"
REGEX_CUSTOMER_NAME = r"Business Name 02: (.*)"
REGEX_INVOICE_NUMBER = r"Invoice No: (\d+)"
REGEX_DATE_ISSUE = r"Date of issue: (\d{2}/\d{2}/\d{4})"
REGEX_DUE_DATE = r"Due Date: (\d{2}/\d{2}/\d{4})"
REGEX_SUBTOTAL = r"Sub total: \$(\d+[,.]\d{2})"
REGEX_DISCOUNT = r"Discount: -\$(\d+[,.]\d{2})"
REGEX_TAX = r"Tax: \$(\d+[,.]\d{2})"
REGEX_TOTAL = r"Total: \$(\d+[,.]\d{2})"

def extract_text_from_invoice_pdf(file_path):
    invoice_data = {
        "business_name": None,
        "customer_name": None,
        "invoice_number": None,
        "date_of_issue": None,
        "due_date": None,
        "subtotal": None,
        "discount": None,
        "tax": None,
        "total": None
    }
    
    try:
        with pdfplumber.open(file_path) as pdf:
            logging.info(f"Processing invoice PDF file: {file_path}")
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
            
            # Estrarre dati dalla fattura con regex
            for key, regex in {
                "business_name": REGEX_BUSINESS_NAME,
                "customer_name": REGEX_CUSTOMER_NAME,
                "invoice_number": REGEX_INVOICE_NUMBER,
                "date_of_issue": REGEX_DATE_ISSUE,
                "due_date": REGEX_DUE_DATE,
                "subtotal": REGEX_SUBTOTAL,
                "discount": REGEX_DISCOUNT,
                "tax": REGEX_TAX,
                "total": REGEX_TOTAL
            }.items():
                match = re.search(regex, text)
                if match:
                    invoice_data[key] = match.group(1)
                    logging.info(f"Found {key}: {invoice_data[key]}")
                else:
                    logging.warning(f"{key} not found in the invoice.")

    except Exception as e:
        logging.error(f"Error processing invoice PDF {file_path}: {e}")
    
    return invoice_data
