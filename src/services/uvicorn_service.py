import uvicorn
from fastapi import FastAPI
from src.query_engine import QueryData
from src.utils.logging import Logger
# from src.utils.evaluation import RagasEval

import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
# APP_FOLDER = os.getenv("APP_FOLDER", "")
# QST_FILE_PATH = os.path.join(APP_FOLDER, 'data/tests/eval_questions.txt')
class UvicornService:
    def __init__(self, rag: QueryData):

        self.query_engine = rag
        self.ragas_eval = None
        self.app = FastAPI()

        # Добавляем эндпоинт в FastAPI
        self.app.add_api_route("/make_query/{query_text}", self.make_query)
        # self.app.add_api_route("/test_rag", self.test_rag)



    async def make_query(self, query_text: str) -> dict:
        # Prepare the DB.
        response = await self.query_engine.take_answer(query_text)

        return response

    # async def test_rag(self) -> dict:
    #     # Prepare the DB.
    #     if self.ragas_eval is None:
    #         self.ragas_eval = RagasEval()
    #     response = await self.ragas_eval.evaluate_rag(self.query_engine)

    #     return response


    def run(self):
        Logger().log('Run the bot')
        """Run application"""
        uvicorn.run(self.app, host="0.0.0.0", port=7007)

# Вне класса
if __name__ == "__main__":
    Logger().log('Starting the bot as __main__ )')
    service = UvicornService()
    service.run()
