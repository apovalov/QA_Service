import logging
import os
from dotenv import load_dotenv, find_dotenv

# Загружаем переменные окружения
load_dotenv(find_dotenv())
app_folder = os.getenv("APP_FOLDER", "")  # Значение по умолчанию - пустая строка, если переменная не найдена

# Путь к файлу лога
log_file_path = os.path.join(app_folder, 'data/logs/raw_logs.log')

def log_init():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        filename=log_file_path)

