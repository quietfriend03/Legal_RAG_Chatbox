from pymilvus import Collection, connections
connections.connect("default", host="localhost", port="19530")  # Ensure this matches your Milvus host/port
collection = Collection("rag_chatbox_db")  # Get an existing collection.
print(collection.num_entities)          # Return the schema of the collection.