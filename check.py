from pymilvus import Collection, connections
connections.connect(alias="default", host="localhost", port="19530")
collection = Collection("rag_chatbox_db")  # Get an existing collection.
collection.num_entities          # Return the number of entities in the collection.
print(collection.num_entities)          # Return the schema of the collection.
