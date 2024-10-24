import os
import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from utils.classification import classify_text
from models.pdf_invoice_model import extract_text_from_invoice_pdf
from models.pdf_resume_model import extract_text_from_resume_pdf
from models.pdf_contract_model import extract_text_from_contract_pdf
from models.pdf_general_model import extract_text_from_pdf
from models.image_model import extract_text_from_image

app = FastAPI()

# Logging
logging.basicConfig(level=logging.DEBUG)

@app.post("/extract_data/")
async def extract_data(file: UploadFile = File(...)):
    file_location = f"temp/{file.filename}"
    
    try:
        with open(file_location, "wb") as f:
            f.write(await file.read())
        
        extracted_data = {}
        
        if file.filename.endswith('.pdf'):
            text = extract_text_from_pdf(file_location)
            if not text:
                raise HTTPException(status_code=400, detail="No text found in PDF.")
            
            classification_result = classify_text(text)['labels'][0]
            
            # Chiama il modello appropriato
            if classification_result == "invoice":
                extracted_data = extract_text_from_invoice_pdf(file_location)
            elif classification_result == "resume":
                extracted_data = extract_text_from_resume_pdf(file_location)
            elif classification_result == "contract":
                extracted_data = extract_text_from_contract_pdf(file_location)
        elif file.filename.endswith(('.jpg', '.jpeg', '.png')):
            extracted_data = extract_text_from_image(file_location)
        else:
            raise HTTPException(status_code=400, detail="File type not supported")

        classification = classify_text(text)

        return {"extracted_data": extracted_data, "classification": classification}

    except Exception as e:
        logging.error(f"Error processing file {file.filename}: {e}")
        raise HTTPException(status_code=500, detail="Error processing the file")

    finally:
        if os.path.exists(file_location):
            os.remove(file_location)

if __name__ == "__main__":
    os.makedirs("temp", exist_ok=True)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
