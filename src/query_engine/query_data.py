from langchain.vectorstores.chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv, find_dotenv
import os
from typing import Tuple, List
from fastapi import HTTPException
import logging
import time
# import tiktoken

class QueryData:
    def __init__(self):

        load_dotenv(find_dotenv())

        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        # CHROMA_PATH = os.getenv("CHROMA_PATH")
        app_folder = os.getenv("APP_FOLDER", "")

        # Путь к файлу лога
        CHROMA_PATH = os.path.join(app_folder, './data/chroma')

        PROMPT_TEMPLATE = """
        Answer the question based only on the following context:

        {context}

        ---

        Answer the question based on the above context: {question}
        """

        self.open_ai_key = OPENAI_API_KEY
        self.chroma_path = CHROMA_PATH
        self.prompt_template = PROMPT_TEMPLATE
        self.db = None # Will be initialized in the prepare_prompt method

    async def prepare_db(self):
        embedding_function = OpenAIEmbeddings(
            model="text-embedding-ada-002", openai_api_key=self.open_ai_key
        )
        db = Chroma(persist_directory=self.chroma_path, embedding_function=embedding_function)
        return db

    async def prepare_prompt(self, query_text: str) -> Tuple[str, List]:
        if not self.db:
            self.db = await self.prepare_db()

        start_time = time.perf_counter()
        results = self.db.similarity_search_with_relevance_scores(query_text, k=3)
        end_time = time.perf_counter()

        logging.info('Similarity search time: %.2f seconds', round(end_time - start_time, 2))
        # logging.info('Similarity scores: %s', [round(score, 2) for _, score in results])

        results = self.db.similarity_search_with_relevance_scores(query_text, k=3)

        # logging.info('Results: %s', results)
        for i, (doc, _score) in enumerate(results):
            logging.info('***')
            logging.info('Document %d [%.2f]: \n %s...%s',i , round(_score, 2),  doc.page_content[:50], doc.page_content[-50:])

        logging.info('Similarity scores: %s', [round(score, 2) for _, score in results])
        if not results or results[0][1] < 0.7:
            raise HTTPException(status_code=404, detail="Matching results not found")
            return

        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
        prompt_template = ChatPromptTemplate.from_template(self.prompt_template)
        prompt = prompt_template.format(context=context_text, question=query_text)

        # request_tokens = tiktoken.count_tokens(prompt)
        # logging.info('Number of tokens in request: %d', request_tokens)

        return prompt, results

    async def get_from_llm(self, prompt: str) -> str:
        start_time = time.perf_counter()
        model = ChatOpenAI(openai_api_key=self.open_ai_key, model="gpt-3.5-turbo")
        response_text = model.invoke(prompt)
        end_time = time.perf_counter()

        logging.info('OpenAI response time: %.2f seconds', round(end_time - start_time, 2))
        return response_text

    # async def get_response(self, query_text: str) -> str:
    #     prompt_start_time = time.perf_counter()
    #     prompt = await self.prepare_prompt(query_text)
    #     # prompt_end_time = time.perf_counter()

    #     response = await self.get_from_llm(prompt)
    #     response_end_time = time.perf_counter()

    #     logging.info('Total request time: %.2f seconds', round(response_end_time - prompt_start_time, 2))
    #     logging.info('Question: %s', query_text)
    #     logging.info('Response: %s', response)

    #     # response_tokens = tiktoken.count_tokens(response)
    #     # logging.info('Number of tokens in response: %d', response_tokens)

    #     formatted_response = f"Prompt: {prompt}\nResponse: {response} \n"
    #     return formatted_response

    async def get_response(self, query_text: str) -> str:
        prompt_start_time = time.perf_counter()
        prompt, results = await self.prepare_prompt(query_text)
        response = await self.get_from_llm(prompt)
        response_end_time = time.perf_counter()

        # Логирование времени выполнения
        logging.info('-------')
        logging.info('Question: %s', query_text)
        logging.info('Response: %s', response)
        # logging.info('-------')
        # logging.info('Similarity search time: %.2f seconds', round(response_end_time - prompt_start_time, 2))
        # logging.info('OpenAI response time: %.2f seconds', round(response_end_time - prompt_start_time, 2))
        # logging.info('Total request time: %.2f seconds', round(response_end_time - prompt_start_time, 2))
        # logging.info('-------')

        # Логирование сокращенных результатов поиска
        # for doc, _score in results:
        #     logging.info('Document: %s...%s', doc.page_content[:50], doc.page_content[-50:])
        #     logging.info('***')

        formatted_response = f"Prompt: {prompt}\nResponse: {response} \n"
        return formatted_response

