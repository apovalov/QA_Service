import logging
import hashlib
import os
from typing import Tuple, Dict, List
from dotenv import load_dotenv, find_dotenv
from .postgre_manager import DatabaseManager
from tiktoken import encoding_for_model

load_dotenv(find_dotenv())
APP_FOLDER = os.getenv("APP_FOLDER", "")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

class Logger:
    def __init__(self):
        # Загружаем переменные окружения

        log_file_path = os.path.join(APP_FOLDER, 'data/logs/raw_logs.log')
        self.init_logger(log_file_path)

    def init_logger(self, log_file_path):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            filename=log_file_path)

        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        logger = logging.getLogger()
        logger.addHandler(handler)

        device = os.getenv("DEVICE", "")

        if device:
            logging.info('DEVICE: %s', device)


    @staticmethod
    def log_query_info(query_text: str,
                    prompt: str,
                    prompt_duration: float,
                    response_duration: float,
                    total_duration: float,
                    response_text: str,
                    token_spents: int,
                    formatted_spents: str,
                    # response_tokens: int=0,
                    scores: str):
        query_hash = hashlib.sha256(query_text.encode()).hexdigest()[:6]


        logging.info('------- // -------')
        logging.info('Prompt preparation time: %.2f seconds', prompt_duration)
        logging.info('OpenAI response time: %.2f seconds', response_duration)
        logging.info('Total request time: %.2f seconds', total_duration)
        logging.info('------- // -------')
        logging.info('Prompt: %s', prompt)
        logging.info('Score: %s', scores)
        logging.info('------- // -------')
        logging.info('Question: %s [%s]', query_text, query_hash)
        logging.info('Response: %s', response_text)
        logging.info('------- // -------')
        logging.info('------- // -------')
        logging.info('Formatted tokens spent: %s', formatted_spents)

        # Инициализируем DatabaseManager и вставляем лог
        db = DatabaseManager()
        db.insert_log(query_text, query_hash, prompt_duration, response_duration, total_duration, response_text, token_spents, prompt, scores)

    # @staticmethod
    # async def log_query_async(prompt: str, response_data: dict, scores: str) -> None:
    #     asyncio.create_task(Logger.log_query_info(response_data['query_text'], prompt, response_data["prompt_time"], response_data["llm_time"],
    #                         response_data["total_time"], response_data["response_text"], response_data["token_spents"], scores))


    @staticmethod
    def calculate_tokens(prompt_text: str, response_text: str) -> Tuple[int, str]:
        encoding = encoding_for_model(MODEL_NAME)
        prompt_tokens = len(encoding.encode(prompt_text))
        response_tokens = len(encoding.encode(response_text))
        token_spents = prompt_tokens + response_tokens
        formatted_spents = f'{token_spents} [{prompt_tokens}, {response_tokens}]'
        return token_spents, formatted_spents

    @staticmethod
    def format_hints(contexts: list, scores: list) -> List[Dict]:
        return [{"document": context, "score": round(score, 2)} for context, score in zip(contexts, scores)]
