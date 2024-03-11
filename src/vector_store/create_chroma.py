from langchain.text_splitter import RecursiveCharacterTextSplitter, SentenceTransformersTokenTextSplitter
from langchain.schema import Document
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.vectorstores.chroma import Chroma
# from langchain.vectorstores.weaviate import Weaviate
import shutil
from langchain_community.document_loaders import DirectoryLoader

from dotenv import load_dotenv, find_dotenv
import os


load_dotenv(find_dotenv())
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMB_MODEL = os.getenv("EMB_MODEL", "text-embedding-ada-002")
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
CHUNK_SIZE = os.getenv("CHUNK_SIZE", 500)
CHUNK_OVERLAP = os.getenv("CHUNK_OVERLAP", 100)


# Путь к файлу лога
APP_FOLDER = os.getenv("APP_FOLDER", "")
CHROMA_PATH = os.path.join(APP_FOLDER, './data/chroma')
WEAVIATE_PATH = os.path.join(APP_FOLDER, './data/weaviate')
DATA_PATH = os.path.join(APP_FOLDER, './data/documents/2021')



def main():
    generate_data_store()


def generate_data_store():
    documents = load_documents()
    chunks = split_text(documents)
    save_to_chroma(chunks)


def load_documents():
    loader = DirectoryLoader(DATA_PATH, glob="*.txt")
    documents = loader.load()
    return documents


def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        add_start_index=True,
    )
    # text_splitter = SentenceTransformersTokenTextSplitter()

    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    document = chunks[10]
    print(document.page_content)
    print(document.metadata)

    return chunks


def save_to_chroma(chunks: list[Document]):
    # Clear out the database first.
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    # Create a new DB from the documents.
    db = Chroma.from_documents(
        chunks,
        OpenAIEmbeddings(model=EMB_MODEL, openai_api_key=OPENAI_API_KEY),
        persist_directory=CHROMA_PATH,
        collection_metadata = {"vs_type": "Chroma",
                               "source": "2021",
                               'splitter': "RecursiveCharacterTextSplitter",
                               "chunk_size": CHUNK_SIZE,
                               "chunk_overlap": CHUNK_OVERLAP,}
    )
    db.persist()
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")


# def save_to_weaviate(chunks: list[Document]):
#     # Clear out the database first.
#     if os.path.exists(WEAVIATE_PATH):
#         shutil.rmtree(WEAVIATE_PATH)

#     # Setup vector database with embedded options
#     client = weaviate.Client(embedded_options=EmbeddedOptions())

#     # Create a new DB from the documents.
#     db = Weaviate.from_documents(
#         client=client,
#         documents=chunks,
#         embedding=OpenAIEmbeddings(model=EMB_MODEL, openai_api_key=OPENAI_API_KEY),
#         collection_metadata={"vs_type": "Weaviate",
#                              "source": "2021",
#                              'splitter': "RecursiveCharacterTextSplitter",
#                              "chunk_size": CHUNK_SIZE,
#                              "chunk_overlap": CHUNK_OVERLAP},
#         by_text=False  # If you're embedding entire documents, set this to True
#     )

#     # db.persist()
#     print(f"Saved {len(chunks)} chunks to {WEAVIATE_PATH}.")


if __name__ == "__main__":
    main()
