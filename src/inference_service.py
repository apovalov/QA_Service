import argparse
from datetime import datetime
from langchain.vectorstores.chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv, find_dotenv
import os
import uvicorn
from fastapi import FastAPI, HTTPException

app = FastAPI()

CHROMA_PATH = "./app/data/chroma"
LOG_FILE = "./app/data/logs/query_logs.txt"
load_dotenv(find_dotenv())
open_ai_key = os.getenv("OPENAI_API_KEY")

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

def log_to_file(request, promt, response):
    with open(LOG_FILE, "a") as log_file:  # Open in append mode
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_file.write(f"Request: {request}\n")
        # log_file.write(f"Promt: {promt}\n")
        log_file.write(f"Response: {response}\n")
        log_file.write(f"Time: {current_time}\n")
        log_file.write("----\n")

@app.get("/make_query/{query_text}")
async def make_query(query_text: str) -> str:
    print(f'1.Begining. query_text: {query_text}')
    # Prepare the DB.
    embedding_function = OpenAIEmbeddings(
        model="text-embedding-ada-002", openai_api_key=open_ai_key
    )
    print('2.Embedding function')
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_relevance_scores(query_text, k=3)
    print('3.Results', results)
    if not results or results[0][1] < 0.7:
        raise HTTPException(status_code=404, detail="Matching results not found")
        return

    print('4.After results')

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    print('5.Prompt')
    model = ChatOpenAI(openai_api_key=open_ai_key, model="gpt-3.5-turbo")
    # prompt = 'What is the capital of France?'
    response_text = model.invoke(prompt)

    print('6.Response', response_text)

    # sources = [doc.metadata.get("source", None) for doc, _score in results]
    # formatted_response = f"Request: {query_text}\nResponse: {response_text}\nSources: {sources}\n"
    formatted_response = f"Promt: {prompt}\nResponse: {response_text} \n"
    print(formatted_response)

    # Log data
    log_to_file(query_text, prompt, response_text)
    return formatted_response


def main() -> None:
    """Run application"""
    uvicorn.run("inference_service:app", host="localhost", port=5000)

if __name__ == "__main__":
    main()
