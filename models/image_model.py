import pytesseract
import cv2

def extract_text_from_image(file_path):
    processed_image = preprocess_image(file_path)
    text = pytesseract.image_to_string(processed_image)
    # Stampa il testo estratto per il debug
    print("Testo estratto:", text)
    
    #text = parse_extracted_data(text)
    return text

def preprocess_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Immagine non trovata o non valida.")
    
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh_image = cv2.threshold(gray_image, 150, 255, cv2.THRESH_BINARY)
    return thresh_image

def parse_extracted_data(text):
    extracted_data = {
        'name': None,
        'phone': None,
        'email': None,
    }

    # Separiamo le linee del testo
    lines = text.split('\n')
    for line in lines:
        # Verifica se la linea contiene un nome
        if 'nome' in line.lower() or 'name' in line.lower():
            extracted_data['name'] = line.strip()
        # Verifica se la linea contiene un telefono
        elif 'telefono' in line.lower() or 'phone' in line.lower():
            extracted_data['phone'] = line.strip()
        # Verifica se la linea contiene un'email
        elif 'email' in line.lower():
            extracted_data['email'] = line.strip()

    print("Dati estratti:", extracted_data)
    return extracted_data

# Esempio di utilizzo
try:
    data = extract_text_from_image("path/to/business-card.jpg")
except Exception as e:
    print(f"Error processing file: {str(e)}")
