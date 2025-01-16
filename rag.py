from pymilvus import Collection, connections
from sentence_transformers import SentenceTransformer
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
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
            ###Instruction\ninstruction:{context} \n\n### Question\nquestion: {query}\n\n### Answer\nanswer: 
        """
            
        Settings.llm = Ollama(model="legalllama", request_timeout=100.0, temperature=0.0)
        answer = Settings.llm.complete(input_text)
        return answer

# Example Usage
# rag = RAG()
# rag.response_generate("Hãy cho tôi biết về luật an ninh mạng")
