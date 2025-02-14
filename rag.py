from pymilvus import Collection, connections
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from reranking import rerank_documents
from query_rewrtiting import generate_rewritten_queries, model as qr_model, tokenizer as qr_tokenizer
import requests

class RAG:
    def __init__(self, collection_name='rag_chatbox_db', vector_model_name='all-MiniLM-L6-v2'):
        # Load the collection and vector model
        connections.connect("default", host="localhost", port="19530")
        self.collection_name = collection_name
        self.collection = Collection(collection_name)
        self.vector_model = SentenceTransformer(vector_model_name)
        
        # Load fine-tuned GPT-2 model
        model_name = "kienhoang123/vietnamese-legal-gpt2"
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.generator = pipeline('text-generation', model=self.model, tokenizer=self.tokenizer)
        self.context = []

    def retrive_relevent_docs(self, query, top_k=10):
        # Generate query variations
        rewritten_queries = generate_rewritten_queries(query, qr_model, qr_tokenizer)
        all_results = []
        
        # Get results for original query
        query_embedding = self.vector_model.encode([query])[0].tolist()
        self.collection.load()
        original_results = self.collection.search(
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
        all_results.extend(original_results[0])
        
        # Get results for each rewritten query
        for rewritten_query in rewritten_queries:
            query_embedding = self.vector_model.encode([rewritten_query])[0].tolist()
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
            all_results.extend(results[0])
        
        return [all_results]  # Maintain the same return format

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
        relevent_docs = self.retrive_relevent_docs(query)
        reranked_results = rerank_documents(query, relevent_docs[0], top_k=2)
        
        # Format context with documents and scores
        contexts = []
        for doc, score in reranked_results:
            contexts.append(f"Document (Relevance Score: {score}):\n{doc}")
        context = "\n\n=== Next Document ===\n\n".join(contexts)
        
        prompt = f"""Hãy trả lời câu hỏi dựa trên các thông tin pháp luật sau đây một cách rõ ràng và chính xác.

        Thông tin pháp luật:
        {context}

        Câu hỏi: {query}

        Trả lời dựa trên các điều luật trên:"""
        # generated_text = self.generator(
        #     prompt,
        #     max_new_tokens=200,
        #     temperature=0.1,
        #     top_p=0.95,
        #     num_beams=4,
        #     pad_token_id=self.tokenizer.eos_token_id,
        # )
        
        # return generated_text[0]['generated_text']

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
        answer = response['response']
        
        return answer