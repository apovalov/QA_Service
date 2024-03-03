from langchain.vectorstores.chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

open_ai_key = os.getenv("OPENAI_API_KEY")
CHROMA_PATH = os.getenv("CHROMA_PATH")

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

async def prepare_db():
    # Prepare the DB.
    embedding_function = OpenAIEmbeddings(
        model="text-embedding-ada-002", openai_api_key=open_ai_key
    )
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    return db

async def prepare_promt(query_text: str) -> str:
    db = await prepare_db()

    # Search the DB.
    results = db.similarity_search_with_relevance_scores(query_text, k=3)
    print('3.Results', results)
    if not results or results[0][1] < 0.7:
        raise Exception(status_code=404, detail="Matching results not found")
        return

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    return prompt

async def get_from_llm(prompt: str) -> str:
    model = ChatOpenAI(openai_api_key=open_ai_key, model="gpt-3.5-turbo")
    response_text = model.invoke(prompt)
    return response_text

async def get_response(query_text: str) -> str:
    prompt = await prepare_promt(query_text)
    response_text = await get_from_llm(prompt)
    formatted_response = f"Promt: {prompt}\nResponse: {response_text} \n"

    return formatted_response