import uvicorn
from fastapi import FastAPI
from src.query_engine import QueryData

class UvicornService:
    def __init__(self):

        self.query_engine = QueryData()
        self.app = FastAPI()

        # Добавляем эндпоинт в FastAPI
        self.app.add_api_route("/make_query/{query_text}", self.make_query)


    async def make_query(self, query_text: str) -> dict:
        # Prepare the DB.
        response = await self.query_engine.take_answer(query_text)

        # Log data
        return response

    def run(self):
        """Run application"""
        uvicorn.run(self.app, host="0.0.0.0", port=7007)

# Вне класса
if __name__ == "__main__":
    service = UvicornService()
    service.run()
