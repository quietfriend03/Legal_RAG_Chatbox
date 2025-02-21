from pymilvus import Collection, connections
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from reranking import rerank_documents
from query_rewrtiting import generate_rewritten_queries, model as qr_model, tokenizer as qr_tokenizer
import requests

class RAG:
    def __init__(self, collection_name='rag_chatbox_db', vector_model_name='all-MiniLM-L6-v2',
                 use_reranking=True, use_query_rewriting=True, top_k=5, model_type="gpt2"):
        # Load the collection and vector model
        connections.connect("default", host="localhost", port="19530")
        self.collection_name = collection_name
        self.collection = Collection(collection_name)
        self.vector_model = SentenceTransformer(vector_model_name)
        
        self.model_type = model_type
        if model_type == "gpt2":
            model_name = "kienhoang123/vietnamese-legal-gpt2"
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.generator = pipeline('text-generation', model=self.model, tokenizer=self.tokenizer)
        
        self.context = []
        self.use_reranking = use_reranking
        self.use_query_rewriting = use_query_rewriting
        self.top_k = top_k

    def retrieve_relevant_docs(self, query, top_k=10):
        query_embedding = self.vector_model.encode([query])[0].tolist()
        self.collection.load()
        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param={
                "metric_type": "COSINE",
                "params": {
                    "ef": 100,
                    "M": 16
                }
            },
            limit=top_k,
            expr=None,
            output_fields=["metadata"]
        )
        return results

    def process_search_results(self, results):
        processed_texts = []
        for hit in results:
            metadata = hit.entity.get('metadata')
            content = metadata.get('chunk_content', '')
            formatted_text = f"Luật: {metadata.get('luật')}\n"
            formatted_text += f"Điều {metadata.get('điều')}: {metadata.get('tên_điều')}\n"
            formatted_text += f"Nội dung: {content}"
            processed_texts.append(formatted_text)
        return processed_texts

    def response_generate(self, query):
        all_results = []
        queries = [query]
        if self.use_query_rewriting:
            rewritten_queries = generate_rewritten_queries(query, qr_model, qr_tokenizer)
            queries.extend(rewritten_queries)

        for q in queries:
            relevant_docs = self.retrieve_relevant_docs(q)
            
            if self.use_reranking:
                reranked_results = rerank_documents(q, relevant_docs[0], top_k=self.top_k)
                all_results.extend(reranked_results)
            else:
                processed_docs = self.process_search_results(relevant_docs[0])
                all_results.extend([(doc, "1.0000") for doc in processed_docs[:self.top_k]])
        
        seen_docs = set()
        unique_results = []
        for doc, score in all_results:
            if doc not in seen_docs:
                seen_docs.add(doc)
                unique_results.append((doc, score))
        
        unique_results.sort(key=lambda x: float(x[1]), reverse=True)
        
        contexts = []
        doc_limit = 1 if self.model_type == "gpt2" else 4
        for doc, score in unique_results[:doc_limit]:
            contexts.append(f"Document (Relevance Score: {score}):\n{doc}")
        context = "\n\n=== Next Document ===\n\n".join(contexts)
        
        prompt = f"""Hãy trả lời câu hỏi dựa trên các thông tin pháp luật sau đây một cách rõ ràng và chính xác.

        Thông tin pháp luật:
        {context}

        Câu hỏi: {query}

        Trả lời dựa trên các điều luật trên:
        """
        
        if self.model_type == "gpt2":
            generated_text = self.generator(
                prompt,
                max_new_tokens=200,
                temperature=0.1,
                top_p=0.95,
                num_beams=4,
                pad_token_id=self.tokenizer.eos_token_id,
            )
            return generated_text[0]['generated_text']
        else:
            payload = {
                "model": "llama3.2",
                "prompt": prompt,
                "context": self.context,
                "stream": False,
            }
            response = requests.post(
                url='http://localhost:11434/api/generate', json=payload
            ).json()
            self.context = response['context']
            return response['response']

# if __name__ == "__main__":
#     rag_gpt2 = RAG(model_type="gpt2", top_k=1)
#     rag_llama = RAG(model_type="llama", top_k=4)
    
#     response = rag_gpt2.response_generate("Luật an ninh mạng là gì")
#     print("GPT-2 Response:", response)
    
    # response = rag_llama.response_generate("Luật an ninh mạng là gì")
    # print("LLaMA Response:", response)