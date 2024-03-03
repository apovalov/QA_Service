# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
#WORKDIR /usr/src/app
WORKDIR /app


# Обновление списка пакетов и установка curl
RUN apt-get update && apt-get install -y curl

# Copy the Python dependencies file into the container at /usr/src/app
COPY requirements.txt ./
RUN python -m pip install --upgrade pip && pip install -r requirements.txt


# Copy the rest of your application's source code from your host to your image filesystem.

COPY src/ ./src
COPY data/chroma app/data/chroma
COPY data/logs app/data/logs

# Inform Docker that the container is listening on the specified port at runtime.
EXPOSE 8000

# Run query_data.py when the container launches
# Note: It's generally not a good practice to run scripts with arguments directly in the Dockerfile,
# because it makes the container less flexible. Instead, you should pass the argument at runtime.
# Run inference_service.py when the container launches
CMD ["uvicorn", "src.inference_service:app", "--host", "0.0.0.0", "--port", "5000"]
#CMD ["uvicorn", "src.inference_service:app", "--port", "8000"]