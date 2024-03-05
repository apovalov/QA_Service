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
from tiktoken import encoding_for_model
from src.logging import Logger
# import hashlib
# import tiktoken

class QueryData:
    def __init__(self):

        load_dotenv(find_dotenv())

        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        app_folder = os.getenv("APP_FOLDER", "")
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

        results = self.db.similarity_search_with_relevance_scores(query_text, k=3)

        Logger.log_search_results(results)

        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
        prompt_template = ChatPromptTemplate.from_template(self.prompt_template)
        prompt = prompt_template.format(context=context_text, question=query_text)

        return prompt, results

    async def get_from_llm(self, prompt: str) -> str:
        model_name = "gpt-3.5-turbo"
        model = ChatOpenAI(openai_api_key=self.open_ai_key, model=model_name)
        response = model.invoke(prompt)
        response_text = response.content

        encoding = encoding_for_model(model_name)
        prompt_tokens = len(encoding.encode(prompt))
        response_tokens = len(encoding.encode(response_text))

        logging.info('Tokens spent: %d [%d, %d]', prompt_tokens+response_tokens, prompt_tokens, response_tokens)
        return response_text

    async def get_response(self, query_text: str) -> str:
        prompt_start_time = time.perf_counter()
        prompt, results = await self.prepare_prompt(query_text)
        prompt_end_time = time.perf_counter()
        response_text = await self.get_from_llm(prompt)
        response_end_time = time.perf_counter()

        Logger.log_query_info(query_text, prompt_start_time, prompt_end_time, response_end_time, response_text)

        formatted_response = f"Prompt: {prompt}\nResponse: {response_text} \n"
        return formatted_response

