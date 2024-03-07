from langchain.vectorstores.chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv, find_dotenv
import os
from typing import Tuple, List
import time
from src.logging import Logger
from tiktoken import encoding_for_model


from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import HumanMessagePromptTemplate, ChatPromptTemplate

from trulens_eval import TruChain


load_dotenv(find_dotenv())

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
APP_FOLDER = os.getenv("APP_FOLDER", "")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
CHROMA_PATH = os.path.join(APP_FOLDER, './data/chroma')

class QueryData:
    def __init__(self):

        self.open_ai_key = OPENAI_API_KEY
        self.chroma_path = CHROMA_PATH
        self.db = None # Will be initialized in the prepare_prompt method

        self.prompt_template = HumanMessagePromptTemplate(
            prompt=PromptTemplate(
                template="Answer the question based only on the following context:\n\n{context}\n\n---\n\nAnswer the question based on the above context: {question}",
                input_variables=["context", "question"]  # Указываем входные переменные
            )
        )

        self.chat_prompt_template = ChatPromptTemplate.from_messages([self.prompt_template])



    async def prepare_db(self):
        embedding_function = OpenAIEmbeddings(
            model="text-embedding-ada-002", openai_api_key=self.open_ai_key
        )
        db = Chroma(persist_directory=self.chroma_path, embedding_function=embedding_function)
        return db



    async def prepare_prompt(self, query_text: str) -> Tuple[str, List, str, str]:
        if not self.db:
            self.db = await self.prepare_db()

        results = self.db.similarity_search_with_relevance_scores(query_text, k=3)
        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])

        prompt = self.chat_prompt_template.format(context=context_text, question=query_text)

        return prompt, results, context_text, query_text



    # async def get_from_llm(self, prompt: str) -> str:
    #     model = ChatOpenAI(openai_api_key=self.open_ai_key, model=MODEL_NAME)
    #     response = model.invoke(prompt)
    #     response_text = response.content

    #     return response_text


    # from langchain.chains import LLMChain
    # from trulens_eval import TruChain

    async def get_from_llm(self, context: str, question: str) -> str:
        # Создание модели ChatOpenAI
        model = ChatOpenAI(openai_api_key=self.open_ai_key, model=MODEL_NAME)

        # Обертывание модели в LLMChain
        llm_chain = LLMChain(llm=model, prompt=self.chat_prompt_template)

        # Обертывание LLMChain в TruChain
        tru_chain = TruChain(llm_chain)

        # Использование TruChain как контекстного менеджера
        # async with tru_chain as recorder:
        #     # Вызов модели через LLMChain
        #     response = await llm_chain.acall({"input": prompt})

        with tru_chain as recording:
            response = llm_chain.invoke({'context':context, 'question': question})

        # print(response)

        response_text = response['text']

        # Получение записи вызова, если это необходимо
        # record = recorder.get()

        return response_text



    async def get_response(self, query_text: str) -> dict:
        prompt_start_time = time.perf_counter()
        prompt, results, context, question = await self.prepare_prompt(query_text)
        prompt_end_time = time.perf_counter()
        response_text = await self.get_from_llm(context, question)
        response_end_time = time.perf_counter()

        prompt_duration = round(prompt_end_time - prompt_start_time, 2)
        response_duration = round(response_end_time - prompt_end_time, 2)
        total_duration = round(response_end_time - prompt_start_time, 2)

        # Вычисляем количество затраченных токенов
        encoding = encoding_for_model(MODEL_NAME)
        prompt_tokens = len(encoding.encode(prompt))
        response_tokens = len(encoding.encode(response_text))
        token_spents = prompt_tokens + response_tokens
        formatted_spents = '%d [%d, %d]' % (token_spents, prompt_tokens, response_tokens)

        scores_str_list = [str(round(score, 2)) for _, score in results]
        scores_str = ", ".join(scores_str_list)

        hints = [{"document": doc.page_content, "score": round(score, 2)} for doc, score in results]

        response_data = {
            "query_text": query_text,
            "response_text": response_text,
            "total_time": total_duration,
            "token_spents": formatted_spents,
            # "scores": scores_str,
            "hints": hints,
            "full_prompt": prompt,
            "prompt_time": prompt_duration,
            "llm_time": response_duration
        }

        Logger.log_query_info(query_text, prompt,
                              prompt_duration,
                              response_duration,
                              total_duration,
                              response_text,
                              prompt_tokens,
                              response_tokens,
                              scores_str)

        return response_data

