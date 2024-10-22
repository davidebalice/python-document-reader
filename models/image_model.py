import pytesseract
import cv2

def extract_text_from_image(file_path):
    processed_image = preprocess_image(file_path)
    text = pytesseract.image_to_string(processed_image)
    return text

def preprocess_image(image_path):
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh_image = cv2.threshold(gray_image, 150, 255, cv2.THRESH_BINARY)
    return thresh_image
