import re
import pdfplumber
import logging

# Espressioni regolari per i campi presenti nel PDF
REGEX_BUSINESS_NAME = r"Company name\s*(.*)"  # Nome azienda
REGEX_CUSTOMER_NAME = r"Company Name\s*(.*)"  # Nome cliente
REGEX_INVOICE_NUMBER = r"Fattura\s+(\d+)"  # Numero fattura
REGEX_DATE_ISSUE = r"Data\s+(\d{2}/\d{2}/\d{4})"  # Data di emissione
REGEX_DUE_DATE = r"Due Date\s+(\d{2}/\d{2}/\d{4})"  # Data di scadenza
REGEX_SUBTOTAL = r"Imponibile\s+€\s*([\d,.]+)"  # Imponibile
REGEX_DISCOUNT = r"Sconto\s+-€\s*([\d,.]+)"  # Sconto
REGEX_TAX = r"IVA\s+€\s*([\d,.]+)"  # IVA
REGEX_TOTAL = r"TOTALE FATTURA\s+€\s*([\d,.]+)"  # Totale fattura

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