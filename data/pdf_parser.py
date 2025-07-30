import fitz  
import re
import os
from config import settings

def clean_text(text: str):
    """Обработка строки"""
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\xa0', ' ', text)
    text = re.sub(r'–\s*Page\s*\d+\s*–', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(\w+)\s*-\s*(\w+)\b', r'\1\2', text)
    text = re.sub(r'\b([А-Яа-яA-Za-zёЁ]+)\s*-\s*([А-Яа-яA-Za-zёЁ]+)\b', r'\1\2', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def extract_title_from_first_page(doc):
    """Извлечение название документа"""
    page = doc[0]
    blocks = page.get_text("dict")["blocks"]
    spans = []

    for block in blocks:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                text = span["text"].strip()
                if not text or len(text) < 5:
                    continue
                size = span["size"]
                y = span["bbox"][1]
                spans.append((size, y, text))

    if not spans:
        return None

    # сортируем по убыванию шрифта, затем по координате Y
    spans.sort(key=lambda x: (-x[0], x[1]))

    # определим максимально крупный размер шрифта
    max_size = spans[0][0]
    top_spans = [s for s in spans if abs(s[0] - max_size) < 0.5 and s[1] < 250]

    # оставим только строки, где текст в верхнем регистре (может быть цифры и знаки)
    uppercase_lines = [s[2] for s in top_spans if s[2].isupper() and len(s[2]) > 10]

    if uppercase_lines:
        title = " ".join(uppercase_lines)
        title = re.sub(r'^УДК\s+[^\s]+\s*(\([^\)]+\))?\s*', '', title, flags=re.IGNORECASE).strip()
        return title

    return None

def extract_url_from_footer(page):
    """Извлечение ссылки на электронный ресурс"""
    page_height = page.rect.height
    blocks = page.get_text("dict")["blocks"]
    
    for block in blocks:
        if block["type"] != 0:
            continue
        x0, y0, x1, y1 = block["bbox"]

        # Только нижние 15% страницы (footer)
        if y0 < 0.85 * page_height:
            continue

        for line in block["lines"]:
            for span in line["spans"]:
                text = span["text"]
                match = re.search(r'https?://\S+|www\.\S+', text)
                if match:
                    return match.group(0)
    return None


def extract_text_from_pdf(pdf_path: str, output_dir: str, one_file: bool = True):
    """Извлечение текста с документа"""
    doc = fitz.open(pdf_path)
    doc_title = extract_title_from_first_page(doc)
    if not doc_title:
        doc_title = os.path.splitext(os.path.basename(pdf_path))[0]

    doc_url = None
    for page in doc:
        doc_url = extract_url_from_footer(page)
        if doc_url:
            break

    os.makedirs(output_dir, exist_ok=True)

    if one_file:
        output_path = os.path.join(output_dir, f"{doc_title}.txt")
        with open(output_path, "w", encoding="utf-8") as f_out:
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_width = page.rect.width
                page_height = page.rect.height
                blocks = page.get_text("dict")["blocks"]
                full_text = ""

                for block in blocks:
                    if block["type"] != 0:
                        continue

                    x0, y0, x1, y1 = block["bbox"]
                    if y0 > 0.9 * page_height:
                        continue
                    if y1 < 0.1 * page_height and x0 > 0.7 * page_width:
                        continue

                    block_text = ""
                    for line in block["lines"]:
                        for span in line["spans"]:
                            font_size = span["size"]
                            if font_size < 6:
                                continue
                            if re.search(r'рис\.|табл\.|figure|table', span["text"], flags=re.IGNORECASE):
                                continue
                            block_text += span["text"] + " "
                    full_text += block_text + "\n"

                cleaned = clean_text(full_text)
                if cleaned:
                    f_out.write(f"Page: {page_num + 1}\n")
                    f_out.write(f"Document Title: {doc_title}\n")
                    if doc_url:
                        f_out.write(f"Document URL: {doc_url}\n")
                    f_out.write(f"Text: {cleaned}" + "\n\n")
    else:
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_width = page.rect.width
            page_height = page.rect.height
            blocks = page.get_text("dict")["blocks"]
            full_text = ""

            for block in blocks:
                if block["type"] != 0:
                    continue

                x0, y0, x1, y1 = block["bbox"]
                if y0 > 0.9 * page_height:
                    continue
                if y1 < 0.1 * page_height and x0 > 0.7 * page_width:
                    continue

                block_text = ""
                for line in block["lines"]:
                    for span in line["spans"]:
                        font_size = span["size"]
                        if font_size < 6:
                            continue
                        if re.search(r'рис\.|табл\.|figure|table', span["text"], flags=re.IGNORECASE):
                            continue
                        block_text += span["text"] + " "
                full_text += block_text + "\n"

            cleaned = clean_text(full_text)
            if cleaned:
                page_path = os.path.join(output_dir, f"{doc_title}_page_{page_num+1}.txt")
                with open(page_path, "w", encoding="utf-8") as f_out:
                    f_out.write(f"Page: {page_num + 1}\n")
                    f_out.write(f"Document Title: {doc_title}\n")
                    if doc_url:
                        f_out.write(f"Document URL: {doc_url}\n")
                    f_out.write(f"Text: {cleaned}" + "\n\n")


def combine_txt_files(path: str):
    """Объединение всех документов в единый"""
    all_text = []
    for filename in os.listdir(path):
        if filename.endswith('.txt'):
            file_path = os.path.join(path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                all_text.append(f.read())
    
    final_path = os.path.join(path, 'final_result.txt')
    with open(final_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_text))

    print(f'Объединённый файл сохранён по пути: {final_path}')


if __name__ == '__main__':

    pdf_dir = settings.DOCS_PATH
    output_dir = settings.EXTRACTED_FILES_PATH
    
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(pdf_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(pdf_dir, filename)
            print(f"Обрабатываю документ: {filename}")
            extract_text_from_pdf(pdf_path, output_dir, one_file=True)
            combine_txt_files(output_dir)