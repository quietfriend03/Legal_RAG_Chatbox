import os
import json
from docx import Document

def read_docx(file_path):
    doc = Document(file_path)
    text = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
    return text

def extract_law_info(text_lines):
    data = []
    current_law, current_chapter, chapter_name = "", "", ""
    current_article, article_title = "", ""
    content, introduction = [], []
    waiting_for_chapter_name, law_found = False, False

    i = 0
    while i < len(text_lines):
        line = text_lines[i]
        if not law_found and "LUẬT" in line.upper():
            current_law, i, law_found = identify_law(text_lines, line, i)
            continue

        if line.startswith("Chương"):
            data, content, current_article = handle_chapter(data, current_law, current_chapter, chapter_name, current_article, article_title, content)
            current_chapter, chapter_name, waiting_for_chapter_name = line, "", True

        elif waiting_for_chapter_name:
            chapter_name, waiting_for_chapter_name = line, False

        elif line.startswith("Điều"):
            data, content = handle_article(data, current_law, current_chapter, chapter_name, current_article, article_title, content)
            current_article, article_title = parse_article(line)

        else:
            introduction, content = handle_content(current_article, introduction, content, line)

        i += 1

    if current_article:
        data.append(create_data_entry(current_law, current_chapter, chapter_name, current_article, article_title, content))

    return data

def identify_law(text_lines, line, i):
    current_law = line
    if i + 1 < len(text_lines) and text_lines[i + 1].isupper():
        current_law += " " + text_lines[i + 1]
        i += 1
    return current_law, i + 1, True

def handle_chapter(data, current_law, current_chapter, chapter_name, current_article, article_title, content):
    if current_article:
        data.append(create_data_entry(current_law, current_chapter, chapter_name, current_article, article_title, content))
    return data, [], ""

def handle_article(data, current_law, current_chapter, chapter_name, current_article, article_title, content):
    if current_article:
        data.append(create_data_entry(current_law, current_chapter, chapter_name, current_article, article_title, content))
    return data, []

def parse_article(line):
    parts = line.split(".", 1)
    return parts[0], parts[1].strip() if len(parts) > 1 else ""

def handle_content(current_article, introduction, content, line):
    if not current_article:
        introduction.append(line)
    else:
        content.append(line)
    return introduction, content

def create_data_entry(current_law, current_chapter, chapter_name, current_article, article_title, content):
    return {
        "luật": current_law,
        "chương": current_chapter,
        "tên_chương": chapter_name,
        "điều": current_article,
        "tên_điều": article_title,
        "nội_dung": "\n".join(content)
    }

def process_folder(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)  

    for file_name in os.listdir(input_folder):
        if file_name.endswith(".docx"):  
            file_path = os.path.join(input_folder, file_name)
            text_lines = read_docx(file_path)
            law_data = extract_law_info(text_lines)

            json_file_name = os.path.splitext(file_name)[0] + ".json"
            json_output_path = os.path.join(output_folder, json_file_name)

            with open(json_output_path, "w", encoding="utf-8") as json_file:
                json.dump(law_data, json_file, ensure_ascii=False, indent=4)


input_folder = "./dataset"  
output_folder = "./data" 

process_folder(input_folder, output_folder)
