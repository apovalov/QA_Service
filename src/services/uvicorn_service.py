from datetime import datetime
from dotenv import load_dotenv, find_dotenv
import uvicorn
from fastapi import FastAPI
from src.query_engine import QueryData
import os

class UvicornService:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.log_file = os.getenv("LOG_FILE")
        self.query_engine = QueryData()
        self.app = FastAPI()

        # Добавляем эндпоинт в FastAPI
        self.app.add_api_route("/make_query/{query_text}", self.make_query)

    def log_to_file(self, request, response):
        with open(self.log_file, "a") as log_file:  # Open in append mode
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            log_file.write(f"Request: {request}\n")
            log_file.write(f"Response: {response}\n")
            log_file.write(f"Time: {current_time}\n")
            log_file.write("----\n")

    async def make_query(self, query_text: str) -> str:
        # Prepare the DB.
        response_text = await self.query_engine.get_response(query_text)

        # Log data
        self.log_to_file(query_text, response_text)
        return response_text

    def run(self):
        """Run application"""
        uvicorn.run(self.app, host="0.0.0.0", port=8000)

# Вне класса
if __name__ == "__main__":
    service = UvicornService()
    service.run()
