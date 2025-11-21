from mistralai import Mistral
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, SparseVectorParams, VectorParams
from dotenv import load_dotenv
from model import get_embedding_model
from typhoon_ocr import ocr_document
import fitz
import time
import base64
import os

load_dotenv()

def pdf_to_markdown(file_path) -> str:
    pdf = fitz.open(file_path)
    num_pages = pdf.page_count
    pdf.close()

    all_page = []
    print(f"--- Processing {file_path} with {num_pages} pages ---") 
    
    for i in range(1, num_pages + 1):
        try:
            markdown = ocr_document(
                pdf_or_image_path=file_path,
                page_num=i
            )
            print(f"Page {i} content length: {len(markdown)}") 
            if len(markdown) < 50:
                print(f"Warning: Page {i} content seems too short: {markdown}")
                
            all_page.append(markdown)
        except Exception as e:
            print(f"Error OCR Page {i}: {e}") 

    return all_page

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
        chunk_size=1000,  
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

def embeded_to_qdrant(file_path):
    try:
        sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")
        embeddings = get_embedding_model()
        markdown = pdf_to_markdown(file_path)
        docs = to_document(markdown) 
        split = split_text(docs)

        url = "http://localhost:6333/"
        client = QdrantClient(url=url)
        if not client.collection_exists("my_documents"):
            client.create_collection(
                collection_name="my_documents",
                vectors_config={
                    "dense": VectorParams(size=768, distance=Distance.COSINE),
                },
                sparse_vectors_config={
                    "sparse": SparseVectorParams(index=models.SparseIndexParams(on_disk=False))
                },
            )
        else:
            client.recreate_collection(
                collection_name="my_documents",
                vectors_config={
                    "dense": VectorParams(size=768, distance=Distance.COSINE),
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