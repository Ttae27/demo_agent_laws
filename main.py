from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from rag.embedding import embeded_to_qdrant
from graph import run_graph
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatInput(BaseModel):
    message: str

@app.post('/upload')
async def get_pdf(file: UploadFile):
    content = await file.read()
    result = embeded_to_qdrant(content)
    return {'message': result}

@app.post('/conversation')
def call_agent(data: ChatInput):
    content = run_graph(data.message)
    return {"message": content}