# Usamos una imagen ligera oficial de Python
FROM python:3.11-slim

# Carpeta de trabajo dentro del servidor
WORKDIR /app

# Copiamos los archivos de tu repositorio
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Exponemos el puerto estándar de Streamlit
EXPOSE 8501

# Comando para encender la app (cambia "app.py" si tu archivo principal tiene otro nombre)
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
