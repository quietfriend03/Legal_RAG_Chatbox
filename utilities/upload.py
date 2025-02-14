from huggingface_hub import HfApi

# Cấu hình thông tin Hugging Face
repo_id = "kienhoang123/VN_legal_framewok"  # Thay bằng tên repo trên Hugging Face
file_path = "../output/vn_legal_framework.json"  # Đường dẫn đến file JSON tổng hợp

# Tạo kết nối API
api = HfApi()

# Tải file lên Hugging Face
api.upload_file(
    path_or_fileobj=file_path,
    path_in_repo="vn_legal_framework.json",  
    repo_id=repo_id,
    repo_type="dataset"
)

print(f"File đã được tải lên Hugging Face: https://huggingface.co/datasets/{repo_id}")
