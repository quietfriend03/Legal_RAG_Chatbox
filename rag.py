from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from bs4 import BeautifulSoup
import requests
import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

class RAG():
    def __init__(self):
        self.vector_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection_name = 'rag_chatbox_db'
        
        # Connect to Milvus Standalone
        connections.connect("default", host="localhost", port="19530")  # Ensure this matches your Milvus host/port

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
        
        self.context = []

    def read_legal_html_to_text(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
        soup = BeautifulSoup(content, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text, os.path.basename(path)
    
    def text_to_docs(self, text, filename):
        if isinstance(text, str):
            text = [text]
        page_docs = [Document(page_content=page) for page in text]
        for i, doc in enumerate(page_docs):
            doc.metadata['page'] = i + 1
            
        doc_chunks = []
        for doc in page_docs:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=4000,
                separators=['\n\n', '\n', '.', ',', '?', '!', ' ', ''],
                chunk_overlap=0.1
            )
            chunk = text_splitter.split_text(doc.page_content)
            for i, chunk in enumerate(chunk):
                doc = Document(
                    page_content=chunk,
                    metadata={"page": doc.metadata['page'], "chunk": i}
                )
                doc.metadata['source'] = (
                    f"{doc.metadata['page']}-{doc.metadata['chunk']}"
                )
                doc.metadata['filename'] = filename
                doc_chunks.append(doc)
        return doc_chunks
    
    def index_docs(self, docs, batch_size=100):
        batch_embeddings = []
        batch_metadata = []
        
        for i, doc in enumerate(docs):
            # Generate embedding for the document
            embedding = self.vector_model.encode([doc.page_content])
            
            metadata = {
                "page": doc.metadata['page'],
                "chunk": doc.metadata['chunk'],
                "filename": doc.metadata['filename'],
                "text": doc.page_content
            }
            
            batch_embeddings.append(embedding[0].tolist())  # Embedding (list of floats)
            batch_metadata.append(metadata)  # Metadata (dict)

            # Insert in batches
            if (i + 1) % batch_size == 0 or i + 1 == len(docs):
                # Insert data into Milvus (embedding and metadata)
                self.collection.insert([batch_embeddings, batch_metadata])  # No need for batch_ids
                batch_embeddings, batch_metadata = [], []

    def create_vectordb(self, paths):
        document = []
        for path in paths:
            text, filename = self.read_legal_html_to_text(path)
            docs = self.text_to_docs(text, filename)
            document.extend(docs)
        self.index_docs(document)
        
    def retrive_relevent_docs(self, query, top_k=10, threshold=0.6):
        query_embedding = self.vector_model.encode([query])[0].tolist()
        self.collection.load()  # Load data into memory
        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param={"metric_type": "L2", "params": {"nprobe": 10}},
            limit=top_k,
            expr=None,
        )
        
        filtered_results = [
            result for result in results[0] if result.score > threshold
        ]
        return filtered_results
    
    def response_generate(self, query):
        relevent_docs = self.retrive_relevent_docs(query)
        context = " ".join(
            [
                match.entity.metadata['text'] for match in relevent_docs if 'text' in match.entity.metadata
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
        response = requests.post(
            url='http://localhost:11434/api/generate', json=payload
        ).json()
        self.context = response['context']
        answer = response['response']
        
        return answer

   
# # Create Vector DB 
rag = RAG()
legal_document_dir = './BoPhapDienDienTu/demuc'
paths = [os.path.join(legal_document_dir, filename) for filename in os.listdir(legal_document_dir) if filename.endswith('.html')]
rag.create_vectordb(paths)

