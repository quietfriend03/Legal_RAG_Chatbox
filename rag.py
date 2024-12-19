from pinecone import Pinecone, ServerlessSpec
from bs4 import BeautifulSoup
import requests
import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
import warnings
load_dotenv()

class RAG():
    def __init__(self):
        self.vector_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.pinecone = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index_name = 'legal-vector-db'
        
        if(self.index_name not in self.pinecone.list_indexes().names()):
            self.pinecone.create_index(
                name=self.index_name,
                dimension=384,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
        self.index = self.pinecone.Index(self.index_name)
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
            doc.metadata['page'] = i+1
            
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
    
    def index_docs(self, docs):
        for doc in docs:
            embedding = self.vector_model.encode([doc.page_content])
            metadata = {
                "page": doc.metadata['page'],
                "chunk": doc.metadata['chunk'],
                "filename": doc.metadata['filename'],
                "text": doc.page_content 
            }
            self.index.upsert(
                vectors=[(doc.metadata['source'], embedding[0].tolist(), metadata)],
            )
            
    def create_vectordb(self, paths):
        document = []
        for path in paths:
            text, filename = self.read_legal_html_to_text(path)
            docs = self.text_to_docs(text, filename)
            document.extend(docs)
        self.index_docs(document)
        
    def retrive_relevent_docs(self, query, top_k=10, threshold=0.6):
        query_embedding = self.vector_model.encode([query])[0].tolist()
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
        )
        filtered_result = [
            match for match in results["matches"] if match['score'] > threshold
        ]
        return filtered_result
    
    def response_generate(self, query):
        relevent_docs = self.retrive_relevent_docs(query)
        context = " ".join(
            [
                match['metadata']['text'] for match in relevent_docs if 'text' in match['metadata']
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
        print(answer)
        return answer
   
# # Create Vector DB 
rag = RAG()
legal_document_dir = './BoPhapDienDienTu/demuc'
paths = [os.path.join(legal_document_dir, filename) for filename in os.listdir(legal_document_dir) if filename.endswith('.html')]
rag.response_generate(query="hãy cho tôi biết về luật an ninh mạng")

