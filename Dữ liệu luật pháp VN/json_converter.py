import os
import json
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

def prettify_xml(elem):
    """Return a pretty-printed XML string."""
    rough_string = ET.tostring(elem, encoding="utf-8")
    parsed = minidom.parseString(rough_string)
    return parsed.toprettyxml(indent="    ")  # 4 spaces indentation


def json_to_xml(json_file, output_folder):
    with open(json_file, "r", encoding="utf-8") as f:
        data_list = json.load(f)
    
    root = ET.Element("CIVIL-CODE")
    ET.SubElement(root, "LAW").text = data_list[0].get("luật", "Không rõ luật")

    # Lấy tên file JSON làm tên file XML
    json_filename = os.path.basename(json_file)
    xml_filename = os.path.splitext(json_filename)[0] + ".xml"
    xml_filepath = os.path.join(output_folder, xml_filename)

    # Thông tin luật
    info = ET.SubElement(root, "INFORMATION")
    ET.SubElement(info, "SOURCE").text = json_filename  # Ghi tên file JSON gốc
    ET.SubElement(info, "YEAR").text = "2025"
    ET.SubElement(info, "LINK").text = "https://thuvienphapluat.vn"
    
    # Nhóm các bài viết theo chương
    chapter_groups = {}
    no_chapter_articles = []  # Lưu các điều không có chương

    for article in data_list:
        chapter_text = article.get("chương", "").strip()
        if chapter_text:
            chapter_parts = chapter_text.split()
            chapter_id = chapter_parts[-1] if chapter_parts else "unknown"
        else:
            chapter_id = "unknown"
        if chapter_id:
            if chapter_id not in chapter_groups:
                chapter_groups[chapter_id] = {
                    "title": article.get("tên_chương", "Không có tên chương"),
                    "articles": []
                }
            chapter_groups[chapter_id]["articles"].append(article)
        else:
            no_chapter_articles.append(article)

    # Thêm các chương và điều luật
    for chapter_id, chapter_data in chapter_groups.items():
        chapter = ET.SubElement(root, "CHAPTER", id=chapter_id)
        ET.SubElement(chapter, "TITLE").text = chapter_data["title"]
        
        for article in chapter_data["articles"]:
            article_id = article.get("điều", "Điều ?").split()[-1]
            article_elem = ET.SubElement(chapter, "ARTICLE", id=article_id)
            ET.SubElement(article_elem, "TITLE").text = article.get("tên_điều", "Không có tiêu đề")
            ET.SubElement(article_elem, "CONTENT").text = article.get("nội_dung", "Không có nội dung")

    # Nếu có điều luật không có chương, thêm trực tiếp vào root
    for article in no_chapter_articles:
        article_id = article.get("điều", "Điều ?").split()[-1]
        article_elem = ET.SubElement(root, "ARTICLE", id=article_id)
        ET.SubElement(article_elem, "TITLE").text = article.get("tên_điều", "Không có tiêu đề")
        ET.SubElement(article_elem, "CONTENT").text = article.get("nội_dung", "Không có nội dung")

    # Lưu file XML
    os.makedirs(output_folder, exist_ok=True)
    tree = ET.ElementTree(root)
    tree.write(xml_filepath, encoding="utf-8", xml_declaration=True)
    print(f"Chuyển đổi {json_filename} -> {xml_filepath} thành công!")


def process_json_files(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            json_file = os.path.join(input_folder, filename)
            json_to_xml(json_file, output_folder)


# Thư mục chứa file JSON đầu vào và thư mục đầu ra XML
input_folder = "./JSON"  # Thư mục chứa các file JSON
output_folder = "./XML"  # Thư mục lưu các file XML

# Xử lý tất cả file JSON trong thư mục
process_json_files(input_folder, output_folder)
