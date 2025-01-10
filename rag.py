from pymilvus import Collection, connections
from sentence_transformers import SentenceTransformer
import requests

class RAG:
    def __init__(self, collection_name='rag_chatbox_db', vector_model_name='all-MiniLM-L6-v2'):
        # Load the collection and vector model
        connections.connect("default", host="localhost", port="19530")
        self.collection_name = collection_name
        self.collection = Collection(collection_name)
        self.vector_model = SentenceTransformer(vector_model_name)
        self.context = []

    def retrive_relevent_docs(self, query, top_k=10, threshold=0):
        query_embedding = self.vector_model.encode([query])[0].tolist()
        self.collection.load()
        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param={"metric_type": "L2", "params": {"nprobe": 10}},
            limit=top_k,
            expr=None,
            output_fields=["metadata"]
        )
        filtered_results = [
            result for result in results[0] if result.score > threshold
        ]
        return filtered_results

    def response_generate(self, query):
        relevent_docs = self.retrive_relevent_docs(query)
        context = " ".join(
            [
                result.entity.metadata.get("text", "") for result in relevent_docs
            ]
        )
        input_text = f"""
            Câu hỏi: {query} 
            Thông tin: {context}
        """
        
        payload = {
            "model": "llama3.2",
            "prompt": input_text,
            "context": self.context,
            "stream": False,
        }
        try:
            response = requests.post(
                url='http://localhost:11434/api/generate', json=payload
            ).json()
            self.context = response['context']
            answer = response['response']
            return answer
        except requests.exceptions.ConnectionError as e:
            print(f"ConnectionError: {e}")
            return None

# Example Usage
# rag = RAG()
# rag.response_generate("Hãy cho tôi biết về luật an ninh mạng")
