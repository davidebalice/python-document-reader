import pdfplumber
import logging

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            logging.info(f"Processing general PDF file: {file_path}")
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text

    except Exception as e:
        logging.error(f"Error processing PDF {file_path}: {e}")
    return text
