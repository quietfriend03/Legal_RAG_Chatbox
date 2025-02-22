import os
import json
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from sentence_transformers import SentenceTransformer
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

class VectorDBIndexer:
    def __init__(self, collection_name, vector_model_name='all-MiniLM-L6-v2'):
        self.vector_model = SentenceTransformer(vector_model_name)
        self.collection_name = collection_name

        # Connect to Milvus Standalone
        connections.connect("default", host="localhost", port="19530")

        # Define schema for Milvus collection
        self.fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=384),
            FieldSchema(name="metadata", dtype=DataType.JSON),
        ]
        self.schema = CollectionSchema(fields=self.fields, description="RAG Vector Store")

        # Check if collection exists; create if not
        if not utility.has_collection(self.collection_name):
            self.collection = Collection(
                name=self.collection_name,
                schema=self.schema,
                consistency_level="Strong",
            )
        else:
            self.collection = Collection(self.collection_name)

    def process_json_data(self, json_file, batch_size=100):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        
        batch_embeddings = []
        batch_metadata = []
        
        for entry in data:
            # Split the content into smaller chunks
            content = entry['nội_dung']
            chunks = text_splitter.split_text(content)
            
            for i, chunk in enumerate(chunks):
                # Create context-aware combined text
                combined_text = f"Luật: {entry['luật']}\nĐiều {entry['điều']}: {entry['tên_điều']}\nPhần {i+1}/{len(chunks)}:\n{chunk}"
                
                # Generate embedding for the combined text
                embedding = self.vector_model.encode([combined_text])
                
                metadata = {
                    "luật": entry['luật'],
                    "điều": entry['điều'],
                    "tên_điều": entry['tên_điều'],
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "chunk_content": chunk
                }
                
                batch_embeddings.append(embedding[0].tolist())
                batch_metadata.append(metadata)
                
                if len(batch_embeddings) >= batch_size:
                    self.collection.insert([batch_embeddings, batch_metadata])
                    batch_embeddings, batch_metadata = [], []
        
        if batch_embeddings:
            self.collection.insert([batch_embeddings, batch_metadata])

    def create_index(self):
        index_params = {
            "index_type": "HNSW",
            "metric_type": "COSINE",
            "params": {
                "M": 16,              # Number of edges per node
                "efConstruction": 200  # Size of the dynamic candidate list
            }
        }
        print("Creating index...")
        self.collection.create_index(field_name="embedding", index_params=index_params)
        print("Index created successfully.")

# Initialize and run indexing
json_file = './Dữ liệu huấn luyện/vn_legal_framework.json'
indexer = VectorDBIndexer(collection_name='rag_chatbox_db')
indexer.process_json_data(json_file)
indexer.create_index()