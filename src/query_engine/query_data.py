from langchain.vectorstores.chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHROMA_PATH = os.getenv("CHROMA_PATH")

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

class QueryData:
    def __init__(self):
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

    async def prepare_prompt(self, query_text: str) -> str:
        if not self.db:
            self.db = await self.prepare_db()

        results = self.db.similarity_search_with_relevance_scores(query_text, k=3)
        print('3.Results', results)
        if not results or results[0][1] < 0.7:
            raise Exception(status_code=404, detail="Matching results not found")
            return

        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
        prompt_template = ChatPromptTemplate.from_template(self.prompt_template)
        prompt = prompt_template.format(context=context_text, question=query_text)
        return prompt

    async def get_from_llm(self, prompt: str) -> str:
        model = ChatOpenAI(openai_api_key=self.open_ai_key, model="gpt-3.5-turbo")
        response_text = model.invoke(prompt)
        return response_text



    async def get_response(self, query_text: str) -> str:
        prompt = await self.prepare_prompt(query_text)
        response_text = await self.get_from_llm(prompt)
        formatted_response = f"Prompt: {prompt}\nResponse: {response_text} \n"
        return formatted_response