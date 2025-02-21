from rag import RAG

rag_gpt2 = RAG(model_type="gpt2", top_k=1)
rag_llama = RAG(model_type="llama", top_k=4)

while True:
    try:
        model_choice = input("Chọn mô hình (1: GPT-2, 2: LLaMA3.2): ")
        if model_choice not in ['1', '2']:
            print("Lựa chọn không hợp lệ. Vui lòng chọn 1 hoặc 2.")
            continue
            
        query = input("Nhập câu hỏi (gõ 'exit' để thoát): ")
        if query.strip().lower() == "exit":
            break
            
        rag_model = rag_gpt2 if model_choice == '1' else rag_llama
        answer = rag_model.response_generate(query)
        print(f"Trả lời: {answer}")
        print()
    except KeyboardInterrupt:
        break