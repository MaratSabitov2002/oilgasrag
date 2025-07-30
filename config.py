import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    # Хранение данных
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    DOCS_PATH: str = os.path.join(BASE_DIR, "data", "documents")
    EXTRACTED_FILES_PATH: str = os.path.join(BASE_DIR, "data", "extracted")
    CHUNKS_JSON_PATH: str = os.path.join(BASE_DIR, "data", "chunks")
    CHROMA_PATH: str = os.path.join(BASE_DIR, "data", "chroma_db")

    # чанки
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 100

    GIGACHAT_API: str

    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env")

settings = Config() 


