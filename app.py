from rag import RAG
rag = RAG()

while True:
    try:
        query = input("Nhập câu hỏi: ")
        if(query.strip() == "exit"):
            break
        answer = rag.response_generate(query)
        print(f"Trả lời: {answer}")
        print()
    except KeyboardInterrupt:
        break