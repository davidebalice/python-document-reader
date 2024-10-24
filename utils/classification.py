import pdfplumber
import logging
from transformers import pipeline
import re

# Modello zero-shot classification con contesto
classifier = pipeline('zero-shot-classification', model='facebook/bart-large-mnli')

def classify_text(text):
    #labels = ["invoice", "resume", "contract", "other"]
    labels = ["invoice", "resume", "contract"]
    # Fornisci una descrizione per aiutare il modello
    descriptions = {
        "invoice": "A document used for billing or financial transactions.",
        "resume": "A document summarizing someone's education, work experience, and skills for job applications.",
        "contract": "A legally binding document outlining the terms of an agreement."
       
    }
    #"other": "A document that doesn't fit any of the other categories."


    # Modifica il testo in base alla descrizione per migliorare la classificazione
    classification = classifier(text, candidate_labels=labels, hypothesis_template="This document is a {}.")
    return classification

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

        # **Pre-elaborazione del testo**: Cerca parole chiave tipiche dei resume
        keywords = ["EDUCATION", "EMPLOYMENT HISTORY", "EXPERIENCE", "SKILLS"]
        relevant_text = "\n".join([line for line in text.splitlines() if any(keyword in line for keyword in keywords)])

        if not relevant_text:  # Se non trovi parole chiave rilevanti, usa tutto il testo
            relevant_text = text

        # **Override della classificazione basata su parole chiave**
        if any(keyword in text for keyword in keywords):
            classification_result = "resume"
        else:
            # Classificazione del testo pre-elaborato o completo con descrizione
            classification_result = classify_text(relevant_text)['labels'][0]

        if classification_result == "resume":
            # Estrarre Nome (esempio: "Homer Simpson")
            name_match = re.search(r"([A-Za-z]+\s[A-Za-z]+)\n", text)
            if name_match:
                resume_data["name"] = name_match.group(1)

            # Estrarre informazioni di contatto (email e telefono)
            contact_match = re.search(r"([A-Za-z0-9\.\-\_]+@[A-Za-z0-9]+\.[A-Za-z]+)", text)
            phone_match = re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
            if contact_match and phone_match:
                resume_data["contact"] = {
                    "email": contact_match.group(1),
                    "phone": phone_match.group(0),
                }

            # Estrarre educazione
            education_match = re.search(r"EDUCATION\n(.+?)\n\n", text, re.DOTALL)
            if education_match:
                resume_data["education"] = education_match.group(1).strip()

            # Estrarre esperienza lavorativa
            employment_history_match = re.search(r"EMPLOYMENT HISTORY\n(.+?)$", text, re.DOTALL)
            if employment_history_match:
                resume_data["employment_history"] = employment_history_match.group(1).strip()

        return {"extracted_data": resume_data, "classification": classification_result}

    except Exception as e:
        logging.error(f"Error processing resume PDF {file_path}: {e}")
        return {"error": f"Error processing the PDF: {str(e)}"}
