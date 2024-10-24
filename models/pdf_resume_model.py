import pdfplumber
import logging
import re

def extract_text_from_resume_pdf(file_path):
    text = ""
    logging.info(f"Processing resume PDF file: {file_path}")
    
    resume_data = {
        "name": None,
        "contact": None,
        "education": None,
        "employment_history": None,
    }

    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text
        
        # Rimuovi spazi bianchi
        text = text.strip()

        if not text:
            logging.warning(f"No text found in resume PDF: {file_path}")
            return {"error": "No text found in the resume."}

        # **Estrarre Nome**: Modifica per estrarre il nome dalla prima riga, cercando il pattern classico di nome completo.
        lines = text.splitlines()
        if len(lines) > 0:
            name_match = re.search(r"^[A-Za-z]+\s[A-Za-z]+$", lines[0])  # Primo nome e cognome nella prima riga
            if name_match:
                resume_data["name"] = name_match.group(0)
            else:
                logging.warning("Name not found")

        # **Estrarre Email e Telefono**
        contact_match = re.search(r"([A-Za-z0-9\.\-\_]+@[A-Za-z0-9\.\-]+\.[A-Za-z]+)", text)
        phone_match = re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
        if contact_match or phone_match:
            resume_data["contact"] = {
                "email": contact_match.group(1) if contact_match else None,
                "phone": phone_match.group(0) if phone_match else None,
            }

        # **Estrarre Educazione**
        # Estrazione migliorata per cercare la sezione EDUCATION e il testo successivo fino a EMPLOYMENT HISTORY
        education_match = re.search(r"EDUCATION\n(.+?)\n(EMPLOYMENT HISTORY|$)", text, re.DOTALL)
        if education_match:
            resume_data["education"] = education_match.group(1).strip()
        else:
            logging.warning("Education not found")

        # **Estrarre Esperienza Lavorativa**
        employment_history_match = re.search(r"EMPLOYMENT HISTORY\s*(.+)$", text, re.DOTALL)
        if employment_history_match:
            resume_data["employment_history"] = employment_history_match.group(1).strip()
        else:
            logging.warning(f"Employment history not found in resume PDF: {file_path}")

        return {"extracted_data": resume_data}

    except Exception as e:
        logging.error(f"Error processing resume PDF {file_path}: {e}")
        return {"error": f"Error processing the PDF: {str(e)}"}
