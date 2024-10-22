from transformers import pipeline

# Specifica esplicitamente il modello per la classificazione
classifier = pipeline('zero-shot-classification', model='facebook/bart-large-mnli')

def classify_text(text):
    labels = ["invoice", "resume", "contract", "other"]
    classification = classifier(text, candidate_labels=labels)
    return classification
