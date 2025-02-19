import pandas as pd
import xml.etree.ElementTree as ET

# Read CSV file with proper column separation
df = pd.read_csv('../csv/data.csv', sep=',', encoding='utf-8')
print("Columns in DataFrame:", df.columns.tolist())

# Create XML structure
root = ET.Element("CIVIL-CODE")

# Add general information
info = ET.SubElement(root, "INFORMATION")
ET.SubElement(info, "NAME").text = "CIVIL CODE"
ET.SubElement(info, "YEAR").text = "2015"
ET.SubElement(info, "LINK").text = "https://thuvienphapluat.vn/van-ban/Quyen-dan-su/Bo-luat-dan-su-2015-296215.aspx"

# Group data by article
for idx, row in df.iterrows():
    conversation = ET.SubElement(root, "CONVERSATION", id=str(idx + 1))
    
    # Add article and chapter information if available
    if 'Điều' in row and pd.notna(row['Điều']):
        conversation.set('article', str(row['Điều']))
    if 'Chương' in row and pd.notna(row['Chương']):
        conversation.set('chapter', str(row['Chương']))

    # Add questions
    questions = ET.SubElement(conversation, "QUESTIONS")
    for col in ["Base Query", "Rewritten 1", "Rewritten 2", "Rewritten 3"]:
        if col in row and pd.notna(row[col]):
            ET.SubElement(questions, "QUESTION").text = str(row[col])

    # Add answers
    answers = ET.SubElement(conversation, "ANSWERS")
    if 'Trả lời' in row and pd.notna(row['Trả lời']):
        ET.SubElement(answers, "ANSWER").text = str(row['Trả lời'])

# Export to XML file
tree = ET.ElementTree(root)
tree.write("output.xml", encoding="utf-8", xml_declaration=True)

print("Conversion complete! output.xml has been created.")
