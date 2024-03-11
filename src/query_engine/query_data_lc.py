import os
import time
import asyncio

from .abstract_rag import RAG
from dotenv import load_dotenv, find_dotenv
# from trulens_eval import TruChain
from langchain.vectorstores.chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from src.utils.logging import Logger
from src.utils.evaluation import TestEngine

from langchain import hub
from langchain.schema import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


load_dotenv(find_dotenv())

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
APP_FOLDER = os.getenv("APP_FOLDER", "")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
EMB_MODEL = os.getenv("EMB_MODEL", "text-embedding-ada-002")
CHROMA_PATH = os.path.join(APP_FOLDER, './data/chroma')



class QueryDataLC(RAG):
    def __init__(self):

        self.tests:TestEngine = None
        self.retriever = None  # Will be initialized in prepare_db
        self.logger = Logger()
        self.llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
        self.prompt = hub.pull("rlm/rag-prompt")
        self.tru_recorder = None


    async def prepare_db(self):
        embedding_function = OpenAIEmbeddings(
            model=EMB_MODEL, openai_api_key=OPENAI_API_KEY
        )
        db = Chroma(persist_directory=CHROMA_PATH,
                    embedding_function=embedding_function)
        return db


    async def take_answer_lc(self, query_text: str) -> dict:
        if not self.retriever:
             db = await self.prepare_db()
             self.retriever = db.as_retriever()

        # prompt = hub.pull("rlm/rag-prompt")
        # llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

        def format_docs(docs):
            contexts =  "\n\n".join(doc.page_content for doc in docs)
            self.contexts = contexts
            return contexts

        rag_chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

        # if not self.tests:
        #     self.tests = TestEngine(rag_chain)

        # if not self.tru_recorder:
        #     self.tru_recorder = TruChain(rag_chain,
        #         app_id='Chain1_ChatApplication',
        #         feedbacks=[self.tests.lc_qa_relevance,
        #                    self.tests.lc_context_relevance,
        #                    self.tests.lc_groundedness])

        # with self.tru_recorder as recording:
        llm_response = rag_chain.invoke(query_text)
        return llm_response



    async def take_answer(self, query_text: str) -> dict:
        prompt_start_time = time.perf_counter()
        # contexts, scores = await self.retrieve_context(query_text)
        # prompt = self.prepare_promt(query_text, contexts)
        # prompt_end_time = time.perf_counter()

        llm_response = await self.take_answer_lc(query_text)
        response_end_time = time.perf_counter()

        # prompt_duration = round(prompt_end_time - prompt_start_time, 2)
        # response_duration = round(response_end_time - prompt_end_time, 2)
        total_duration = round(response_end_time - prompt_start_time, 2)

        token_spents, formatted_spents = self.logger.calculate_tokens(self.contexts, llm_response)
        # hints = Logger.format_hints(contexts, scores)

        response_data = {
            "query_text": query_text,
            "response_text": llm_response,
            "total_time": total_duration,
            "token_spents": formatted_spents,
            "hints": self.contexts,
            "prompt_time": 0,
            "llm_time": 0,
            "rag_config": self.logger.rag_config
        }

        asyncio.create_task(self.log_query_info("", response_data, "", token_spents))
        return response_data



    async def log_query_info(self, prompt: str, response_data: dict, scores: str, token_spents: int) -> None:
        self.logger.log_query_info(response_data['query_text'], prompt, response_data["prompt_time"], response_data["llm_time"],
                            response_data["total_time"], response_data["response_text"],token_spents, response_data["token_spents"], scores)



