from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

def get_embedding_model():
    return GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

def get_llm():
    return ChatGoogleGenerativeAI(model="gemini-2.5-pro")