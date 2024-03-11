import os
from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv, find_dotenv
from src.query_engine import QueryData
from src.utils.logging import Logger

load_dotenv(find_dotenv())
APP_TOKEN = os.environ.get("APP_TOKEN")

class TG_Service:

    def __init__(self, rag: QueryData):
        self.query_engine = rag
        self.bot = Bot(token=APP_TOKEN)
        self.dp = Dispatcher(self.bot)

        # Registering the message handler using a method
        self.dp.register_message_handler(self.take_answer)

    async def take_answer(self, message: types.Message):
        query_text = message.text
        response = await self.query_engine.take_answer(query_text)
        text_respone = response['response_text']

        Logger().log(f'TGResponse:, {response}')
        # await message.answer(response)
        await message.reply(text_respone)
        # await message.answer(response['scores'])

    def run(self):
        """Run application"""
        Logger().log('Run the bot')
        executor.start_polling(self.dp)

if __name__ == "__main__":
    # Initialize QueryData here (or pass an initialized instance)
    rag = QueryData()
    tg_service = TG_Service(rag)
    tg_service.run()  # This method starts the bot
