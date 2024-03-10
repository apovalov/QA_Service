from abc import ABC, abstractmethod

class RAG(ABC):

    @abstractmethod
    async def take_answer(self, query_text: str) -> dict:
        return {}
