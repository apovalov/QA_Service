import psycopg2
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

class DatabaseManager:
    def __init__(self):
        self.conn = self.connect_db()
        self.create_table()

    @staticmethod
    def connect_db():
        """ Создает подключение к базе данных """
        try:
            conn = psycopg2.connect(DATABASE_URL)
            print("К базе подключились")
            return conn
        except psycopg2.DatabaseError as e:
            print(f"Ошибка подключения к базе данных: {e}")
            return None

    def create_table(self):
        """ Создает таблицу для логов, если она еще не существует """
        create_table_query = """
            CREATE TABLE IF NOT EXISTS query_logs (
                id SERIAL PRIMARY KEY,
                created_at TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP,
                total_time FLOAT,
                token_spents INT,
                query_text TEXT,
                response_text TEXT,
                scores TEXT,
                qa_relevance FLOAT,
                context_relevance FLOAT,
                groundedness FLOAT,
                rag_config TEXT,
                prompt TEXT,
                prompt_time FLOAT,
                response_time FLOAT,
                query_hash TEXT
            )
        """
        cursor = self.conn.cursor()
        cursor.execute(create_table_query)
        self.conn.commit()
        print('Таблица создана')
        cursor.close()

    # def insert_log(self, query_text, query_hash, prompt_time, response_time, total_time, response_text, token_spents, promt, scores):
    #     """ Вставляет запись лога в таблицу """
    #     insert_query = """
    #         INSERT INTO query_logs (query_text, query_hash, prompt_time, response_time, total_time, response_text, token_spents, promt, scores)
    #         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    #     """
    #     cursor = self.conn.cursor()
    #     cursor.execute(insert_query, (query_text, query_hash, prompt_time, response_time, total_time, response_text, token_spents, promt, scores))
    #     self.conn.commit()
    #     cursor.close()

    def insert_log(self, total_time, token_spents, query_text, response_text, scores, qa_relevance, context_relevance, groundedness, rag_config, prompt, prompt_time, response_time, query_hash):
        """ Вставляет запись лога в таблицу """
        insert_query = """
            INSERT INTO query_logs (total_time, token_spents, query_text, response_text, scores, qa_relevance, context_relevance, groundedness, rag_config, prompt, prompt_time, response_time, query_hash)
            VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor = self.conn.cursor()
        cursor.execute(insert_query, (total_time, token_spents, query_text, response_text, scores, qa_relevance, context_relevance, groundedness, rag_config, prompt, prompt_time, response_time, query_hash))
        self.conn.commit()
        cursor.close()


    def __del__(self):
        """ Закрывает соединение с базой данных """
        if self.conn is not None:
            self.conn.close()

# Использование класса DatabaseManager
# db_manager = DatabaseManager()
# db_manager.create_table()
# Пример добавления записи в лог
# db_manager.insert_log("Пример запроса", "hash", 0.1, 0.2, 0.3, "Ответ", 123, "Пример prompt")
