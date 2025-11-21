from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from rag.embedding import embeded_to_qdrant
from graph import run_graph
from pydantic import BaseModel
from typing import List, Dict, Any
import shutil
import os

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
    mode: str = "general"
    history: List[Dict[str, Any]] = []

@app.post('/upload')
async def get_pdf(file: UploadFile):
    file_location = f"uploads/{file.filename}"

    for f in os.listdir("uploads"):
        file_path = os.path.join("uploads", f)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

    with open(file_location, "wb") as file_object:
        shutil.copyfileobj(file.file, file_object)
    result = embeded_to_qdrant(file_location)
    return {'message': result}

@app.post('/conversation')
def call_agent(data: ChatInput):
    content = run_graph(data.message, data.mode, data.history)
    return {"message": content}