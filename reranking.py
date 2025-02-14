from sentence_transformers import CrossEncoder

class Reranker:
    def __init__(self, model_name='cross-encoder/ms-marco-MiniLM-L-6-v2', max_length=512):
        self.model = CrossEncoder(model_name, max_length=max_length)

    def rerank(self, query, documents, top_k):
        truncated_docs = [doc[:800] if len(doc) > 800 else doc for doc in documents]
        pairs = [[query, doc] for doc in truncated_docs]
        scores = self.model.predict(pairs)
        
        doc_score_pairs = list(zip(documents, scores))
        reranked_docs = sorted(doc_score_pairs, key=lambda x: x[1], reverse=True)
        
        # Return both documents and scores
        return [(doc, f"{score:.4f}") for doc, score in reranked_docs[:top_k]]

def format_document(metadata):
    content = metadata.get('chunk_content', '')
    if len(content) > 800:
        content = content[:797] + "..."
    
    return (
        f"{metadata.get('luật')}\n"
        f"{metadata.get('điều', '')}: {metadata.get('tên_điều', '')}\n"
        f"Nội dung: {content}"
    )

def process_hits(hits):
    documents = []
    for hit in hits:
        metadata = hit.entity.get('metadata')
        if metadata:
            formatted_doc = format_document(metadata)
            documents.append(formatted_doc)
    return documents

def rerank_documents(query, hits, top_k):
    reranker = Reranker()
    documents = process_hits(hits)
    reranked_docs = reranker.rerank(query, documents, top_k)
    return reranked_docs