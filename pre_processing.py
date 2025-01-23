import os
from bs4 import BeautifulSoup
import re

class PreProcessingData:
    def __init__(self, save_dir):
        self.save_dir = save_dir
        # Automatically create the folder if it doesn't exist
        os.makedirs(save_dir, exist_ok=True)

    def read_legal_html_to_text(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
        soup = BeautifulSoup(content, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()
        text = re.sub(r'(?<!\()Chương\s+([IVXLCDM]+|\d+)', r'\n\g<0>', text)
        text = re.sub(r'(?<!\()Điều\s+\d+', r'\n\g<0>', text)
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        # Save extracted text to a .txt file
        filename = os.path.basename(path).replace('.html', '.txt')
        save_path = os.path.join(self.save_dir, filename)
        with open(save_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(text)

        return save_path  # Return the path to the saved text file

    def convert_html_to_text_files(self, html_paths):
        txt_files = []
        for path in html_paths:
            txt_file = self.read_legal_html_to_text(path)
            txt_files.append(txt_file)
        return txt_files


html_dir = './BoPhapDienDienTu/demuc'  # Directory containing the HTML files
output_dir = './processed_vn_legal_document'                # Directory to save the converted text files

# List of HTML file paths
html_paths = [os.path.join(html_dir, filename) for filename in os.listdir(html_dir) if filename.endswith('.html')]

# Convert HTML to Text Files
converter = PreProcessingData(save_dir=output_dir)
txt_files = converter.convert_html_to_text_files(html_paths)
