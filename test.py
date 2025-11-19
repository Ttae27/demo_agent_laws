from model import get_embedding_model, get_llm
from langchain_qdrant import QdrantVectorStore

embeddings = get_embedding_model()

vector_store = QdrantVectorStore.from_existing_collection(
    embedding=embeddings,
    collection_name="my_documents",
    url="http://localhost:6333",
)

results = vector_store.similarity_search(
    "ในหน้าที่ 4 พูดเกี่ยวกับอะไร", k=4
)
for res in results:
    print(f"* {res.page_content} [{res.metadata}]")