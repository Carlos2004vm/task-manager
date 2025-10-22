# Imagen base de Python 3.11 (versión ligera)
FROM python:3.11-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar el archivo de dependencias
COPY requirements.txt .

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código de la aplicación al contenedor
COPY ./app /app

# Exponer el puerto 8000 para la API
EXPOSE 8000

# Comando para iniciar el servidor FastAPI con recarga automática
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

RUN pip install --no-cache-dir openpyxl pandas python-multipart