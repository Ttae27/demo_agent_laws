from model import get_embedding_model
from langchain_qdrant import QdrantVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

@tool
def query_rag(query_text):
    """
    Retrieve documents using RAG (Retrieval-Augmented Generation)
    and generate a formatted prompt containing the most relevant content.

    Args:
        query_text (str): The user's question or search related to the documents.

    Returns:
        str: A fully formatted prompt containing top-ranked context documents and the original question.
            This prompt can be passed to an LLM for final answer generation.
    """

    PROMPT_TEMPLATE = """
    Answer the question based only on the following context:
    {context}
    - -
    Answer the question based on the above context: {question}
    """

    embeddings = get_embedding_model()

    vector_store = QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        collection_name="my_documents",
        url="http://localhost:6333",
    )

    results = vector_store.similarity_search(query_text, k=4)

    # for res in results:
    #     print('-'*100)
    #     print(f"* {res.page_content}")

    context_text = "\n\n - -\n\n".join([str(doc.page_content) for doc in results])

    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    return prompt