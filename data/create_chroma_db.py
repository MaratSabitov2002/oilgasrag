import json
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_gigachat.embeddings import GigaChatEmbeddings
from config import settings

def generate_chroma_db(json_name: str):
    """Создание векторной базы данных"""

    with open(settings.CHUNKS_JSON_PATH+"/"+json_name, "r", encoding="utf-8") as f:
        chunks_data = json.load(f)

    texts = [item["text"] for item in chunks_data]
    metadatas = [{"title": item["title"], "url": item["url"], "page": item["page"]} for item in chunks_data]
    ids = [item["id"] for item in chunks_data]

    documents = [
        Document(
            page_content=text,
            metadata={
                "title": meta["title"],
                "url": meta["url"],
                "page": meta["page"],
                "id": chunk_id
            }
        )
        for text, meta, chunk_id in zip(texts, metadatas, ids)
    ]

    vectorstore = Chroma.from_documents(
        documents,
        embedding = GigaChatEmbeddings(
            credentials=settings.GIGACHAT_API, scope="GIGACHAT_API_PERS", verify_ssl_certs=False,
        ),
        persist_directory=settings.CHROMA_PATH
    )
    
    print("База Chroma инициализирована")


if __name__ == "__main__":
    generate_chroma_db(json_name="chunks.json")