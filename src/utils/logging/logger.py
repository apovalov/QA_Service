import logging
import hashlib
import os
from typing import Tuple, Dict, List
from dotenv import load_dotenv, find_dotenv
from .postgre_manager import DatabaseManager
from tiktoken import encoding_for_model
import json
# from ipytree import Tree, Node

load_dotenv(find_dotenv())
APP_FOLDER = os.getenv("APP_FOLDER", "")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
EMB_MODEL = os.getenv("EMB_MODEL", "text-embedding-ada-002")

def singleton(class_):
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


@singleton
class Logger:

    rag_config = {
        'vs_type': "Chroma",
        'emb_model': EMB_MODEL,
        'llm_model': MODEL_NAME,
        'rag_type': "QueryData",
        'chunk_type': "RecursiveCharacterTextSplitter",
        'chunk_size': "300",
        'chunk_overlap': "100",
        }

    def __init__(self):
        self.config = {}

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



    def log(self, message: str):
        logging.info(message)

    def log_query_info(self, query_text: str,
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
        # db.insert_log(query_text, query_hash, prompt_duration, response_duration, total_duration, response_text, token_spents, prompt, scores)
        qa_relevance=-1
        context_relevance=-1
        groundedness=-1

        rag_config = json.dumps(self.rag_config)
        db.insert_log(total_duration, token_spents, query_text, response_text, scores, qa_relevance, context_relevance, groundedness, rag_config, prompt, prompt_duration, response_duration, query_hash)

    # @staticmethod
    # async def log_query_async(prompt: str, response_data: dict, scores: str) -> None:
    #     asyncio.create_task(Logger.log_query_info(response_data['query_text'], prompt, response_data["prompt_time"], response_data["llm_time"],
    #                         response_data["total_time"], response_data["response_text"], response_data["token_spents"], scores))

    def calculate_tokens(self, prompt_text: str, response_text: str) -> Tuple[int, str]:
        encoding = encoding_for_model(MODEL_NAME)
        prompt_tokens = len(encoding.encode(prompt_text))
        response_tokens = len(encoding.encode(response_text))
        token_spents = prompt_tokens + response_tokens
        formatted_spents = f'{token_spents} [{prompt_tokens}, {response_tokens}]'
        return token_spents, formatted_spents

    def format_hints(self, contexts: list, scores: list) -> List[Dict]:
        return [{"document": context, "score": round(score, 2)} for context, score in zip(contexts, scores)]

    # def display_call_stack(data):
    #     tree = Tree()
    #     tree.add_node(Node('Record ID: {}'.format(data['record_id'])))
    #     tree.add_node(Node('App ID: {}'.format(data['app_id'])))
    #     tree.add_node(Node('Cost: {}'.format(data['cost'])))
    #     tree.add_node(Node('Performance: {}'.format(data['perf'])))
    #     tree.add_node(Node('Timestamp: {}'.format(data['ts'])))
    #     tree.add_node(Node('Tags: {}'.format(data['tags'])))
    #     tree.add_node(Node('Main Input: {}'.format(data['main_input'])))
    #     tree.add_node(Node('Main Output: {}'.format(data['main_output'])))
    #     tree.add_node(Node('Main Error: {}'.format(data['main_error'])))

    #     calls_node = Node('Calls')
    #     tree.add_node(calls_node)

    #     for call in data['calls']:
    #         call_node = Node('Call')
    #         calls_node.add_node(call_node)

    #         for step in call['stack']:
    #             step_node = Node('Step: {}'.format(step['path']))
    #             call_node.add_node(step_node)
    #             if 'expanded' in step:
    #                 expanded_node = Node('Expanded')
    #                 step_node.add_node(expanded_node)
    #                 for expanded_step in step['expanded']:
    #                     expanded_step_node = Node('Step: {}'.format(expanded_step['path']))
    #                     expanded_node.add_node(expanded_step_node)

    #     return tree

    # def log_record(rec):
    #     tree = self.display_call_stack(rec)
    #     logging.info(tree)