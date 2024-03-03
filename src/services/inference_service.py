from datetime import datetime
from dotenv import load_dotenv, find_dotenv
import uvicorn
from fastapi import FastAPI, HTTPException
from src.query_engine import get_response
import os

app = FastAPI()

load_dotenv(find_dotenv())

LOG_FILE = os.getenv("LOG_FILE")


def log_to_file(request, promt, response):
    with open(LOG_FILE, "a") as log_file:  # Open in append mode
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_file.write(f"Request: {request}\n")
        log_file.write(f"Response: {response}\n")
        log_file.write(f"Time: {current_time}\n")
        log_file.write("----\n")

@app.get("/make_query/{query_text}")
async def make_query(query_text: str) -> str:
    # Prepare the DB.
    # embedding_function = OpenAIEmbeddings(
    #     model="text-embedding-ada-002", openai_api_key=open_ai_key
    # )
    # db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    #
    # # Search the DB.
    # results = db.similarity_search_with_relevance_scores(query_text, k=3)
    # print('3.Results', results)
    # if not results or results[0][1] < 0.7:
    #     raise HTTPException(status_code=404, detail="Matching results not found")
    #     return
    #
    # context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    # prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    # prompt = prompt_template.format(context=context_text, question=query_text)
    #
    # model = ChatOpenAI(openai_api_key=open_ai_key, model="gpt-3.5-turbo")
    # prompt = 'What is the capital of France?'
    # response_text = model.invoke(prompt)
    response_text = await get_response(query_text)

    # formatted_response = f"Promt: {prompt}\nResponse: {response_text} \n"

    # Log data
    # log_to_file(query_text, prompt, response_text)
    return response_text #formatted_response


def main() -> None:
    """Run application"""
    uvicorn.run("inference_service:app", host="localhost", port=8000)

if __name__ == "__main__":
    main()
