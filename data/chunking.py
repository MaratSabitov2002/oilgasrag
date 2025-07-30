import os
import uuid
import json
import re
from typing import List, Dict
from config import settings


def clean_chunk_boundaries(text: str, is_first: bool, is_last: bool) -> str:
    """Выделение чанка с целыми словами"""
    # Обрезаем начало, если не первый чанк
    if not is_first:
        first_space = text.find(" ")
        text = text[first_space + 1:] if first_space != -1 else ""

    # Обрезаем конец, если не последний чанк
    if not is_last:
        last_space = text.rfind(" ")
        text = text[:last_space] if last_space != -1 else ""

    return text.strip()


def parse_txt_file(file_path: str, chunk_size: int = 500, overlap: int = 100) -> List[Dict]:
    """Извлечение текста и метаданных"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pages = re.split(r'\n(?=Page: \d+)', content)
    parsed_pages = []

    for page in pages:
        page_num_match = re.search(r'Page:\s*(\d+)', page)
        title_match = re.search(r'Document Title:\s*(.+)', page)
        url_match = re.search(r'Document URL:\s*(.+)', page)
        text_match = re.search(r'Text:\s*(.+)', page, re.DOTALL)

        if page_num_match and title_match and url_match and text_match:
            parsed_pages.append({
                "page": int(page_num_match.group(1)),
                "title": title_match.group(1).strip(),
                "url": url_match.group(1).strip(),
                "text": text_match.group(1).strip()
            })

    # Собираем весь текст и карту страниц
    full_text = ""
    page_map = []

    for p in parsed_pages:
        start = len(full_text)
        full_text += p['text'] + " "
        end = len(full_text)
        page_map.append((start, end, p['page']))

    # Разбивка на чанки с границами по словам
    chunks = []
    i = 0
    text_len = len(full_text)

    while i < text_len:
        raw_chunk = full_text[i:i + chunk_size]
        is_first = (i == 0)
        is_last = (i + chunk_size >= text_len)

        chunk_text = clean_chunk_boundaries(raw_chunk, is_first, is_last)
        chunk_start = i
        chunk_end = i + len(raw_chunk)

        pages_in_chunk = set()
        for start, end, page_num in page_map:
            if not (chunk_end <= start or chunk_start >= end):
                pages_in_chunk.add(page_num)

        if not pages_in_chunk:
            i += chunk_size - overlap
            continue

        page_list = sorted(pages_in_chunk)
        page_str = str(page_list[0]) if len(page_list) == 1 else f"{page_list[0]}-{page_list[-1]}"

        chunks.append({
            "id": str(uuid.uuid4()),
            "title": parsed_pages[0]['title'],
            "url": parsed_pages[0]['url'],
            "page": page_str,
            "text": chunk_text
        })

        i += chunk_size - overlap

    return chunks


def process_all_txt_files(input_folder: str, output_json: str, chunk_size: int = 500, overlap: int = 100):
    """Процесс генерации чанков по всем документам"""
    all_chunks = []
    name = "chunks.json"
    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            file_path = os.path.join(input_folder, filename)
            print(f"Processing: {filename}")
            file_chunks = parse_txt_file(file_path, chunk_size, overlap)
            all_chunks.extend(file_chunks)

    # Сохраняем все чанки в один JSON
    with open(output_json + "/" + name, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    print(f"\n Всего чанков сохранено: {len(all_chunks)} в файл: {output_json}")


if __name__  == "__main__":
    process_all_txt_files(
        input_folder=settings.EXTRACTED_FILES_PATH,
        output_json=settings.CHUNKS_JSON_PATH,
        chunk_size=settings.CHUNK_SIZE,
        overlap=settings.CHUNK_OVERLAP
    )
