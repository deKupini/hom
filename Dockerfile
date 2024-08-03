# Używamy obrazu bazowego z Pythonem
FROM python:3.9-slim

# Ustawiamy katalog roboczy
WORKDIR /app

# Kopiujemy plik requirements.txt do katalogu roboczego
COPY requirements.txt .

# Instalujemy zależności
RUN pip install --no-cache-dir -r requirements.txt

# Kopiujemy resztę kodu aplikacji do katalogu roboczego
COPY . .

# Ustawiamy zmienne środowiskowe
ENV SECRET_KEY=${SECRET_KEY}
ENV KEYCLOAK_SERVER_URL=${KEYCLOAK_SERVER_URL}
ENV KEYCLOAK_CLIENT_ID=${KEYCLOAK_CLIENT_ID}
ENV KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
ENV KEYCLOAK_REALM=${KEYCLOAK_REALM}

# Uruchamiamy aplikację FastAPI przy użyciu Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]