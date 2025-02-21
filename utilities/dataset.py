import os
import json

# Thư mục chứa các file JSON đầu vào
input_folder = "../Dữ liệu luật pháp VN/JSON"  # Đổi thành thư mục chứa JSON

# Tên file JSON đầu ra
output_json_path = "../Dữ liệu huấn luyện/vn_legal_framework.json"

# Đảm bảo rằng thư mục đầu ra tồn tại
output_dir = os.path.dirname(output_json_path)
os.makedirs(output_dir, exist_ok=True)

# Danh sách chứa tất cả nội dung từ các file JSON
merged_data = []

for file_name in os.listdir(input_folder):
    if file_name.endswith(".json"):
        file_path = os.path.join(input_folder, file_name)
        
        with open(file_path, "r", encoding="utf-8") as json_file:
            try:
                data = json.load(json_file)
                merged_data.extend(data)  # Gộp nội dung vào danh sách tổng hợp
            except json.JSONDecodeError as e:
                print(f"Lỗi khi đọc file JSON {file_path}: {e}")

# Ghi file JSON tổng hợp (sẽ tự động tạo hoặc ghi đè)
with open(output_json_path, "w", encoding="utf-8") as json_out:
    json.dump(merged_data, json_out, ensure_ascii=False, indent=4)

print(f"Đã tạo hoặc ghi đè file JSON tổng hợp: {output_json_path}")