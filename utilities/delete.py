from pymilvus import MilvusClient

client = MilvusClient(
    uri="http://localhost:19530",
    token="root:Milvus"
)

client.drop_collection(
    collection_name="rag_chatbox_db"
)

