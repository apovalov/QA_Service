import logging
import hashlib
import os
from dotenv import load_dotenv, find_dotenv
from .postgre_manager import DatabaseManager

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
                    prompt_tokens: int,
                    response_tokens: int,
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

        token_spents = prompt_tokens + response_tokens

        logging.info('Tokens spent: %d [%d, %d]', token_spents, prompt_tokens, response_tokens)

        # Инициализируем DatabaseManager и вставляем лог
        db = DatabaseManager()
        db.insert_log(query_text, query_hash, prompt_duration, response_duration, total_duration, response_text, token_spents, prompt, scores)

# Пример использования
# logger = Logger()
# logger.log_query_info("Пример запроса", start_time, end_time, end_time, "Ответ")
