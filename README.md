# QA_Service

QAService is a template for deploying a QA system using RAG technology on a remote server.
https://www.google.com/url?sa=i&url=https%3A%2F%2Fblogs.nvidia.com%2Fblog%2Fwhat-is-retrieval-augmented-generation%2F&psig=AOvVaw1Evq2f-XIJKilOCxL2G-FB&ust=1710481546848000&source=images&cd=vfe&opi=89978449&ved=0CBMQjRxqFwoTCPDP6rmG84QDFQAAAAAdAAAAABAJ![Uploading image.png…]()


To deploy the service you need to have Docker compose installed:

1. Upload documents to the documents folder
2. python create_chroma.py
3. Fill in the ```.env``` (at a minimum ```OPENAI_API_KEY```)
4. Copy everything to the remote server 
5. ```docker-compose up -d -build```

Depending on how start.py is configured, you may be able to run
- ```UvicornService``` - RestAPI 
- ```TG_Service``` - Telegram bot
- ```ST_Service``` - StreamLit

You can customize the RAG system by changing:
- The way of reading and splitting documents (by ```RecursiveCharacterTextSplitter```)
- Choose a different VectorStore (default is ```ChormaDB```)
- Choose a different Embedding model (default ```text-embedding-3-small```)
- Select a different retriever method 
- Select a different LLM (optional ```gpt-3.5-turbo```)

Query information is logged to PosgresQL database, with PGAdmin interface.

Also based on TruLens and Ragas, tracking of system parameters is implemented:
- ```context_relevance, answer_relevance, groundedness```
- ```context_precision, context_recall, faithfulness, answer_relevancy```




