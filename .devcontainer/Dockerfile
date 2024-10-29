# Usa una imagen base de Python
FROM python:3.8-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo requirements.txt en el contenedor
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todos los archivos de la app en el contenedor
COPY . .

# Expone el puerto en el que Streamlit ejecuta la app
EXPOSE 8501

# Comando para ejecutar la aplicación
CMD ["streamlit", "run", "agricultura.py", "--server.port=8501", "--server.enableCORS=false"]
