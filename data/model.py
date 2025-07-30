from typing import Any, Dict, List, Literal, Optional
from config import settings
from promts import SYSTEM_PROMPT
from langchain_chroma import Chroma
from langchain_gigachat.embeddings import GigaChatEmbeddings
from langchain_gigachat.chat_models import GigaChat




class ChatWithAI:
    def __init__(self, provider: Literal["gigachat-lite", "gigachat-pro", "gigachat-max"] = "gigachat-lite",
                temperature: float = 0.7, max_tokens: int = 512):
        
        self.provider = provider
        self.embeddings = GigaChatEmbeddings(
            credentials=settings.GIGACHAT_API, 
            scope="GIGACHAT_API_PERS", 
            verify_ssl_certs=False
        )

        models = {
            "gigachat-lite": "GigaChat",
            "gigachat-pro": "GigaChat-Pro",
            "gigachat-max": "GigaChat-Max",
        }

        if provider in models:
            self.llm = GigaChat(
                credentials=settings.GIGACHAT_API, 
                verify_ssl_certs=False,
                model=models[provider],
                # temperature=self.temperature,
                # max_tokens=self.max_tokens
            )
        else:
            raise ValueError(f"Неподдерживаемый провайдер: {provider}")

        self.chroma_db = Chroma(
            persist_directory=settings.CHROMA_PATH,
            embedding_function=self.embeddings,
        )
    
    def get_relevant_context(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Получение релевантного контекста из базы данных."""
        try:
            embedded_query = self.embeddings.embed_query(query)
            results = self.chroma_db.similarity_search_by_vector(embedded_query, k=k)
            return [
                {
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                }
                for doc in results
            ]
        except Exception as e:
            print(f"Ошибка при получении контекста: {e}")
            return []
        
    def format_context(self, context: List[Dict[str, Any]]) -> str:
        """Форматирование контекста для промпта."""
        formatted_context = []
        for item in context:
            metadata_str = "\n".join(f"{k}: {v}" for k, v in item["metadata"].items())
            formatted_context.append(
                f"Текст: {item['text']}\nМетаданные:\n{metadata_str}\n"
            )
        return "\n---\n".join(formatted_context)
    

    def generate_response(self, query: str) -> Optional[str]:
        """Генерация ответа на основе запроса и контекста."""
        try:
            context = self.get_relevant_context(query)
            if not context:
                return "Извините, не удалось найти релевантный контекст для ответа."

            formatted_context = self.format_context(context)

            messages = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": f"Вопрос: {query}\nКонтекст: {formatted_context}",
                },
            ]
            response = self.llm.invoke(messages)
            if hasattr(response, "content"):
                return str(response.content)
            return str(response).strip()
        except Exception as e:
            print(f"Ошибка при генерации ответа: {e}")
            return "Произошла ошибка при генерации ответа."
        

if __name__ == "__main__":
    chat = ChatWithAI(provider="gigachat-pro")
    print("\n=== Чат с ИИ ===\n")

    while True:
        query = input("Вы: ")
        if query.lower() == "выход":
            print("\nДо свидания!")
            break

        print("\nИИ печатает...", end="\r")
        response = chat.generate_response(query)
        print(" " * 20, end="\r") 
        print(f"ИИ: {response}\n")