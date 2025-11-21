from fastapi import FastAPI, UploadFile, BackgroundTasks
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

process = "idle"

def process_embedding(file_path: str):
    global process
    embeded_to_qdrant(file_path)
    process = "done"

@app.post('/upload')
async def get_pdf(file: UploadFile, background_task: BackgroundTasks):
    global process
    process = "processing"
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

    background_task.add_task(process_embedding, file_location)

    return {'message': "waiting for embedd"}

@app.post('/conversation')
async def call_agent(data: ChatInput):
    content = run_graph(data.message, data.mode, data.history)
    return {"message": content}

@app.post('/status')
async def status():
    return {"message": process}

@app.get('/reset_status')
async def reset_status():
    global process
    process = "idle"
    return {"message": "complete reset"}