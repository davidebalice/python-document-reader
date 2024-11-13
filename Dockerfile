# Usa un'immagine base Python
FROM python:3.10-slim

# Imposta la directory di lavoro
WORKDIR /app

# Copia i file richiesti
COPY . .

# Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# Espone la porta su cui FastAPI sarà in ascolto
EXPOSE 8000

# Comando per avviare l'applicazione
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
