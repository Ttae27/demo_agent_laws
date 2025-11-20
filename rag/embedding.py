from mistralai import Mistral
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, SparseVectorParams, VectorParams
from dotenv import load_dotenv
from model import get_embedding_model
import base64
import os

load_dotenv()
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')

def encode_byte(file):
    try:
        return base64.b64encode(file).decode('utf-8')
    except:
        return None

def pdf_to_markdown_MistralOCR(file_data) -> str:
    client = Mistral(api_key=MISTRAL_API_KEY)
    base64_pdf = encode_byte(file_data)
    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": f"data:application/pdf;base64,{base64_pdf}" 
        },
        include_image_base64=True
    )
    all_page = [page.markdown for page in ocr_response.pages]
    return  all_page

def to_document(markdowns: list[str]):
    docs = []
    for i, md in enumerate(markdowns):
        docs.append(Document(
            page_content=md,
            metadata={'page': i + 1}
        ))
    return docs

def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,  
        chunk_overlap=100, 
        length_function=len,
    )
    print(f"text splitter: {text_splitter}")

    chunks = text_splitter.split_documents(documents)
    for chunk in chunks:
        page_num = chunk.metadata['page']
        chunk.page_content = f'# page: {page_num}\n' + chunk.page_content

    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    return chunks  

def embeded_to_qdrant(file_data):
    try:
        sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")
        embeddings = get_embedding_model()
        markdown = pdf_to_markdown_MistralOCR(file_data)
        docs = to_document(markdown) 
        split = split_text(docs)

        url = "http://localhost:6333/"
        client = QdrantClient(url=url)
        if not client.collection_exists("my_documents"):
            client.create_collection(
                collection_name="my_documents",
                vectors_config={
                    "dense": VectorParams(size=3072, distance=Distance.COSINE),
                },
                sparse_vectors_config={
                    "sparse": SparseVectorParams(index=models.SparseIndexParams(on_disk=False))
                },
            )
        else:
            client.recreate_collection(
                collection_name="my_documents",
                vectors_config={
                    "dense": VectorParams(size=3072, distance=Distance.COSINE),
                },
                sparse_vectors_config={
                    "sparse": SparseVectorParams(index=models.SparseIndexParams(on_disk=False))
                },
            )
        vector_store = QdrantVectorStore(
            client=client,
            collection_name="my_documents",
            embedding=embeddings,
            sparse_embedding=sparse_embeddings,
            retrieval_mode=RetrievalMode.HYBRID,
            vector_name="dense",
            sparse_vector_name="sparse",
        )
        vector_store.add_documents(split)

        return 'Successfully embeded'
    except Exception as e:
        return f'Failed to embeded: {e}'