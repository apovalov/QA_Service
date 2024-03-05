# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# ENV CHROMA_PATH="./app/data/chroma"
# ENV LOG_FILE="./app/data/logs/query_logs.txt"
ENV APP_FOLDER="./app"

# Обновление списка пакетов и установка curl
RUN apt-get update && apt-get install -y curl \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*


# Copy the Python dependencies file into the container at /usr/src/app
COPY requirements.txt ./
RUN python -m pip install --upgrade pip && pip install -r requirements.txt



# Copy the rest of your application's source code from your host to your image filesystem.

COPY src/ ./src
COPY start.py ./
COPY data/chroma app/data/chroma
COPY data/logs app/data/logs

# Inform Docker that the container is listening on the specified port at runtime.
EXPOSE 7000

# Run query_data.py when the container launches

#CMD ["uvicorn", "src.services.inference_service:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["python", "start.py"]