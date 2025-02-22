import os
import pandas as pd
import xml.etree.ElementTree as ET

# Định nghĩa hàm chuyển CSV thành XML
def csv_to_xml(input_csv, output_folder):
    # Đọc file CSV
    df = pd.read_csv(input_csv, sep=',', encoding='utf-8')
    print(f"Đang xử lý: {input_csv} - Các cột: {df.columns.tolist()}")

    # Tạo cấu trúc XML
    root = ET.Element("CIVIL-CODE")

    # Thông tin chung
    info = ET.SubElement(root, "INFORMATION")
    ET.SubElement(info, "NAME").text = "CIVIL CODE"
    ET.SubElement(info, "YEAR").text = "2015"
    ET.SubElement(info, "LINK").text = "https://thuvienphapluat.vn/van-ban/Quyen-dan-su/Bo-luat-dan-su-2015-296215.aspx"

    # Duyệt qua từng dòng dữ liệu
    for idx, row in df.iterrows():
        conversation = ET.SubElement(root, "CONVERSATION", id=str(idx + 1))
        
        # Thêm thông tin điều luật nếu có
        if 'Điều' in row and pd.notna(row['Điều']):
            conversation.set('article', str(row['Điều']))
        if 'Chương' in row and pd.notna(row['Chương']):
            conversation.set('chapter', str(row['Chương']))

        # Thêm câu hỏi
        questions = ET.SubElement(conversation, "QUESTIONS")
        for col in ["Base Query", "Rewritten 1", "Rewritten 2", "Rewritten 3"]:
            if col in row and pd.notna(row[col]):
                ET.SubElement(questions, "QUESTION").text = str(row[col])

        # Thêm câu trả lời
        answers = ET.SubElement(conversation, "ANSWERS")
        if 'Trả lời' in row and pd.notna(row['Trả lời']):
            ET.SubElement(answers, "ANSWER").text = str(row['Trả lời'])

    # Tạo thư mục nếu chưa có
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Xuất file XML với tên giống file CSV
    xml_filename = os.path.splitext(os.path.basename(input_csv))[0] + ".xml"
    xml_filepath = os.path.join(output_folder, xml_filename)
    tree = ET.ElementTree(root)
    tree.write(xml_filepath, encoding="utf-8", xml_declaration=True)

    print(f"Chuyển đổi {input_csv} -> {xml_filepath} thành công!")

# Hàm xử lý tất cả các file CSV trong thư mục
def process_csv_folder(input_folder, output_folder):
    if not os.path.exists(input_folder):
        print("Thư mục đầu vào không tồn tại!")
        return
    
    for filename in os.listdir(input_folder):
        if filename.endswith(".csv"):
            csv_file = os.path.join(input_folder, filename)
            csv_to_xml(csv_file, output_folder)

# Định nghĩa thư mục đầu vào và đầu ra
input_folder = "./CSV"  # Thư mục chứa các file CSV
output_folder = "./XML"  # Thư mục lưu các file XML

# Xử lý tất cả file CSV trong thư mục
process_csv_folder(input_folder, output_folder)
