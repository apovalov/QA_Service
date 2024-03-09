from langchain.embeddings import OpenAIEmbeddings
from langchain.evaluation import load_evaluator
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMB_MODEL = os.getenv("EMB_MODEL", "text-embedding-ada-002")

def main():
    # Get embedding for a word.
    embedding_function = OpenAIEmbeddings(
        model=EMB_MODEL, openai_api_key=OPENAI_API_KEY
    )
    vector = embedding_function.embed_query("apple")
    print(f"Vector for 'apple': {vector}")
    print(f"Vector length: {len(vector)}")

    # Compare vector of two words
    evaluator = load_evaluator("pairwise_embedding_distance")
    words = ("apple", "iphone")
    x = evaluator.evaluate_string_pairs(prediction=words[0], prediction_b=words[1])
    print(f"Comparing ({words[0]}, {words[1]}): {x}")


if __name__ == "__main__":
    main()
