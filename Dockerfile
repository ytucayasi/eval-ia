# Usamos una imagen base de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Instalar dependencias desde requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar los archivos de la aplicación (aunque luego los montaremos como volumen)
COPY . .

# Exponer el puerto 8000 (el puerto que utilizará FastAPI)
EXPOSE 8000

# Comando para iniciar la aplicación con recarga automática de Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
