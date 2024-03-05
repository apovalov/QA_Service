import logging
import hashlib
import os
from dotenv import load_dotenv, find_dotenv
from .postgre_manager import DatabaseManager


class Logger:
    def __init__(self):
        # Загружаем переменные окружения
        load_dotenv(find_dotenv())
        app_folder = os.getenv("APP_FOLDER", "")  # Значение по умолчанию - пустая строка, если переменная не найдена

        # Путь к файлу лога
        log_file_path = os.path.join(app_folder, 'data/logs/raw_logs.log')
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
    def log_query_info(query_text: str, prompt_start_time: float, prompt_end_time: float, response_end_time: float, response_text: str):
        query_hash = hashlib.sha256(query_text.encode()).hexdigest()[:6]

        db = DatabaseManager()
        db.insert_log(query_text, query_hash, prompt_end_time - prompt_start_time, response_end_time - prompt_end_time, response_end_time - prompt_start_time, response_text)

        logging.info('------- // -------')
        logging.info('Promt preparation time: %.2f seconds', round(prompt_end_time - prompt_start_time, 2))
        logging.info('OpenAI response time: %.2f seconds', round(response_end_time - prompt_end_time, 2))
        logging.info('Total request time: %.2f seconds', round(response_end_time - prompt_start_time, 2))
        logging.info('------- // -------')
        logging.info('Question: %s [%s]', query_text, query_hash)
        logging.info('Response: %s', response_text)
        logging.info('------- // -------')
        logging.info('------- // -------')

    @staticmethod
    def log_search_results(results):
        logging.info('\nSimilarity scores: %s', [round(score, 2) for _, score in results])
        for i, (doc, _score) in enumerate(results):
            logging.info('*********************\n*** Document %d [%.2f]: ***', i, round(_score, 2))
            logging.info('%s...%s', doc.page_content[:50], doc.page_content[-50:])
            logging.info('*********************')

# Пример использования
# logger = Logger()
# logger.log_query_info("Пример запроса", start_time, end_time, end_time, "Ответ")
