# Xây dựng mô hình hỏi-đáp về Luật dựa trên RAG
## Giới thiệu đề tài
Mô hình hỏi-đáp luật dựa trên RAG là một trong những mô hình để có giúp người dùng hỏi đáp những vấn đề liên quan đến pháp luật Việt Nam, giúp cải thiện khả năng hiểu biết của người dùng về luật pháp của Việt Nam. 
## Yêu cầu cho dự án
- Python 3.12.+
- Docker Desktop
## Cài đặt môi trường
### 1. Cài đặt các thư viện cần thiết
Để có thể cài đặt thư viện cần thiết ta sẽ cần khởi tạo env cho môi thư mục code của chúng ta bằng câu lệnh sau:
```sh
python3 -m venv myenv
source myenv/bin/activate
```
Sau đó ta sẽ xài lệnh sau để tải các module cần thiết cho dự án:
```sh
pip install -r requirements.txt
```
### 2. Cài đặt Ollama
**MacOS và Windows**: Đối với hệ điều hành MacOS và Windows, bạn có thể cài đặt Ollama thông qua trang website chính thức của Ollama theo [<u>link</u>](https://ollama.com/download). 
**Linux**: Đối với hệ điều hành Linux, bạn có thể cài đặt Ollama bằng cách sử dụng câu lệnh sau:
```sh
curl -fsSL https://ollama.com/install.sh | sh
```
### 3. Cài đặt Milvus database 
Để có thể cài đặt được Milvus database, bạn cần cài đặt Docker Desktop trên máy tính của bạn. Sau đó, bạn có thể sử dụng câu lệnh sau để cài đặt Milvus database phiên bản Standalone bằng các câu lệnh sau:
```sh
# Download the installation script
curl -sfL https://raw.githubusercontent.com/milvus-io/milvus/master/scripts/standalone_embed.sh -o standalone_embed.sh

# Start the Docker container
bash standalone_embed.sh start
```
## Chạy ứng dụng
### 1. Khởi tạo mô hình trong Ollama
Để có thể chạy mô hình trong Ollama, ta cần thực hiện tải về trên Ollama thông qua câu lệnh trên trang web của Ollama, ở đây ta sẽ tải mô hình Llama v3.2 theo đường [<u>link</u>](https://ollama.com/library/llama3.2).
Tiếp theo ta có thể tải mô hình Llama v3.2 theo số lượng Parameter mà ta mong muốn là 3B hay 1B tuỳ theo nhu câu:
```sh
# Pulling and running Llama 3.2 3B
ollama pull llama3.2
ollama run llama3.2
```

```sh
# Pulling and running Llama 3.2 1B
ollama pull llama3.2:1b
ollama run llama3.2:1b
```
### 2. Index dữ liệu lên Milvus database
Để có thể thêm dữ liệu vào cơ sỡ dữ liệu vector,đầu tiên ta cần phải đảm bảo container của Milvus đang chạy sau đó ta cần phải chạy theo các lệnh sau:
```sh
python indexing.py
```
Trong lúc đó, hệ thống sẽ tự động indexing từng dữ liệu vào vector database, nếu muốn kiểm tra bao nhiêu dữ liệu đã được index, ta có thể sử dụng câu lệnh sau:
```sh
cd utilities
python entities.py
```
### 3. Chạy mô hình
Sau khi hoàn tất tải dữ liệu cũng như đảm bảo rằng mô hình của chúng ta đã chạy, ta có thể chạy ứng dụng bằng cách sử dụng câu lệnh sau:
```sh
python app.py
```
