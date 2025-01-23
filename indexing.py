import os
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

    def text_to_docs(self, text, filename):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1024,
            separators=['\n\n', '\n', '.', ',', '?', '!', ' ', ''],
            chunk_overlap=0.1
        )
        chunks = text_splitter.split_text(text)
        doc_chunks = []
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "chunk": i,
                    "source": f"{filename}-{i}",
                    "filename": filename
                }
            )
            doc_chunks.append(doc)
        return doc_chunks

    def index_docs(self, txt_dir, batch_size=100):
        legal_files = [os.path.join(txt_dir, f) for f in os.listdir(txt_dir) if f.endswith('.txt')]
        batch_embeddings = []
        batch_metadata = []

        for txt_file in legal_files:
            with open(txt_file, 'r', encoding='utf-8') as file:
                text = file.read()

            docs = self.text_to_docs(text, os.path.basename(txt_file))
            for doc in docs:
                # Generate embedding for the document
                embedding = self.vector_model.encode([doc.page_content])

                metadata = {
                    "chunk": doc.metadata['chunk'],
                    "filename": doc.metadata['filename'],
                    "text": doc.page_content
                }
                batch_embeddings.append(embedding[0].tolist())  # Embedding (list of floats)
                batch_metadata.append(metadata)  # Metadata (dict)

                # Insert in batches
                if len(batch_embeddings) >= batch_size:
                    self.collection.insert([batch_embeddings, batch_metadata])
                    batch_embeddings, batch_metadata = [], []

        # Insert remaining documents
        if batch_embeddings:
            self.collection.insert([batch_embeddings, batch_metadata])

    def create_index(self):
        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "COSINE",
            "params": {"nlist": 128},
        }
        print("Creating index...")
        self.collection.create_index(field_name="embedding", index_params=index_params)
        print("Index created successfully.")

txt_dir = './processed_vn_legal_document'
indexer = VectorDBIndexer(collection_name='rag_chatbox_db')
indexer.index_docs(txt_dir=txt_dir)
indexer.create_index()


