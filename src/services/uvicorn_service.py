import uvicorn
from fastapi import FastAPI
from src.query_engine import RAG

import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
APP_FOLDER = os.getenv("APP_FOLDER", "")
QST_FILE_PATH = os.path.join(APP_FOLDER, 'data/tests/eval_questions.txt')
class UvicornService:
    def __init__(self, rag: RAG):

        self.query_engine = rag
        self.app = FastAPI()

        # Добавляем эндпоинт в FastAPI
        self.app.add_api_route("/make_query/{query_text}", self.make_query)


    async def make_query(self, query_text: str) -> dict:
        # Prepare the DB.
        response = await self.query_engine.take_answer(query_text)

        return response

    def run(self):
        """Run application"""
        uvicorn.run(self.app, host="0.0.0.0", port=7007)

# Вне класса
if __name__ == "__main__":
    service = UvicornService()
    service.run()
