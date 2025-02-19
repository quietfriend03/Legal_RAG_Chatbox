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
    
    # Create a dictionary to group articles by law name
    law_groups = {}
    
    # Process each article in the list
    for article_data in data_list:
        law_name = article_data.get("luật", "Unknown Law")
        if law_name not in law_groups:
            law_groups[law_name] = []
        law_groups[law_name].append(article_data)
    
    # Create separate XML files for each law
    for law_name, articles in law_groups.items():
        root = ET.Element("CIVIL-CODE")
        
        # Thông tin luật
        info = ET.SubElement(root, "INFORMATION")
        ET.SubElement(info, "NAME").text = law_name
        ET.SubElement(info, "YEAR").text = "2025"
        ET.SubElement(info, "LINK").text = "https://thuvienphapluat.vn"
        
        # Group articles by chapter
        chapter_groups = {}
        for article in articles:
            chapter_id = article.get("chương", "Chương ?").split()[-1]
            if chapter_id not in chapter_groups:
                chapter_groups[chapter_id] = {
                    'title': article.get("tên_chương", "Không có tên chương"),
                    'articles': []
                }
            chapter_groups[chapter_id]['articles'].append(article)
        
        # Create chapters and articles
        for chapter_id, chapter_data in chapter_groups.items():
            chapter = ET.SubElement(root, "CHAPTER", id=chapter_id)
            ET.SubElement(chapter, "TITLE").text = chapter_data['title']
            
            # Add articles to chapter
            for article_data in chapter_data['articles']:
                article_id = article_data.get("điều", "Điều ?").split()[-1]
                article = ET.SubElement(chapter, "ARTICLE", id=article_id)
                ET.SubElement(article, "TITLE").text = article_data.get("tên_điều", "Không có tiêu đề")
                ET.SubElement(article, "CONTENT").text = article_data.get("nội_dung", "Không có nội dung")
        
        # Create XML file for this law
        xml_filename = f"{law_name.replace(' ', '_')}.xml"
        xml_filepath = os.path.join(output_folder, xml_filename)
        
        # Write XML file
        tree = ET.ElementTree(root)
        tree.write(xml_filepath, encoding="utf-8", xml_declaration=True)
        print(f"Chuyển đổi các điều luật của {law_name} -> {xml_filepath} thành công!")

def process_json_files(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            json_file = os.path.join(input_folder, filename)
            json_to_xml(json_file, output_folder)

# Thư mục chứa file JSON đầu vào và thư mục đầu ra XML
input_folder = "../Dữ liệu đã xử lí"  # Thư mục chứa các file JSON
output_folder = "../xml"  # Thư mục lưu các file XML

# Xử lý tất cả file JSON trong thư mục
process_json_files(input_folder, output_folder)
