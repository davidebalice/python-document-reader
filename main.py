import pdfplumber
import pytesseract
import cv2
import os
import shutil
import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from transformers import pipeline
import uvicorn
from pdf2image import convert_from_path
import numpy as np



logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),  # Scrive i log su un file
        logging.StreamHandler()            # Mostra i log anche nella console
    ]
)


app = FastAPI()

# Configurazione del logging
logging.basicConfig(level=logging.DEBUG)

# Funzione per leggere i PDF
def extract_text_from_pdf(file_path):
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            total_pages = len(pdf.pages)
            logging.info(f"Processing PDF file: {file_path} with {total_pages} pages.")

            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text() or ""
                if page_text:
                    text += page_text
                    logging.info(f"Extracted text from page {i + 1} (length: {len(page_text)})")
                else:
                    logging.warning(f"Page {i + 1} is empty or not readable.")

            if not text:
                logging.warning("No text extracted from the entire PDF.")
    except Exception as e:
        logging.error(f"Error reading PDF file {file_path}: {e}")
    return text


# Funzione per fare OCR su immagini JPG
def extract_text_from_image(file_path):
    processed_image = preprocess_image(file_path)
    text = pytesseract.image_to_string(processed_image)
    return text

# Preprocessing dell'immagine
def preprocess_image(image_path):
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh_image = cv2.threshold(gray_image, 150, 255, cv2.THRESH_BINARY)
    return thresh_image

# Funzione di classificazione (Machine Learning) su testo
classifier = pipeline('zero-shot-classification')

def classify_text(text):
    labels = ["invoice", "resume", "contract", "other"]
    classification = classifier(text, candidate_labels=labels)
    return classification

# API per upload file e estrazione dati
@app.post("/extract_data/")
async def extract_data(file: UploadFile = File(...)):
    file_location = f"temp/{file.filename}"
    
    try:
        with open(file_location, "wb") as f:
            f.write(await file.read())
        
        if file.filename.endswith('.pdf'):
            text = extract_text_from_pdf(file_location)
            if not text:
                text = extract_text_from_pdf_with_ocr(file_location)
        elif file.filename.endswith(('.jpg', '.jpeg', '.png')):
            text = extract_text_from_image(file_location)
        else:
            raise HTTPException(status_code=400, detail="File type not supported")

        classification = classify_text(text)

        return {"extracted_text": text, "classification": classification}

    except Exception as e:
        logging.error(f"Error processing file {file.filename}: {e}")
        raise HTTPException(status_code=500, detail="Error processing the file")

    finally:
        if os.path.exists(file_location):
            os.remove(file_location)

if __name__ == "__main__":
    os.makedirs("temp", exist_ok=True)
    uvicorn.run(app, host="0.0.0.0", port=8000)
