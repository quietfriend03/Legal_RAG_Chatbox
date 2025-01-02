from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from bs4 import BeautifulSoup
import os
from sentence_transformers import SentenceTransformer
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

class VectorDBCreator:
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
                chunk_size=1024,
                separators=['\n\n', '\n', '.', ',', '?', '!', ' ', ''],
                chunk_overlap=0.1
            )
            chunks = text_splitter.split_text(doc.page_content)
            for i, chunk in enumerate(chunks):
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
                self.collection.insert([batch_embeddings, batch_metadata])
                batch_embeddings, batch_metadata = [], []

    def create_index(self):
        index_params = {
            "index_type": "IVF_FLAT",  # Choose an appropriate index type, e.g., IVF_FLAT, IVF_SQ8, HNSW
            "metric_type": "L2",       # L2 for Euclidean distance or IP for cosine similarity
            "params": {"nlist": 128},  # Number of clusters
        }
        print("Creating index...")
        self.collection.create_index(field_name="embedding", index_params=index_params)
        print("Index created successfully.")

    def create_vectordb(self, paths):
        document = []
        for path in paths:
            text, filename = self.read_legal_html_to_text(path)
            docs = self.text_to_docs(text, filename)
            document.extend(docs)
        self.index_docs(document)
        self.create_index()  # Create index after inserting documents

# # Usage example
# db_creator = VectorDBCreator(collection_name='rag_chatbox_db')
# legal_document_dir = './BoPhapDienDienTu/demuc'
# paths = [os.path.join(legal_document_dir, filename) for filename in os.listdir(legal_document_dir) if filename.endswith('.html')]
# # Create the vector database
# db_creator.create_vectordb(paths)
