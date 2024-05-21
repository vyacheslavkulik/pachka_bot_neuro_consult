import os
from fastapi import FastAPI, Request
import uvicorn
import json
import requests
from pachka import Pachka
from chunk import Chunk
from dotenv import load_dotenv

# получим переменные окружения из .env
load_dotenv()

app = FastAPI()
pachkaDef = Pachka()
chunk = Chunk(path_to_base=os.environ.get("PATH_TO_BASE"))

@app.post("/api/webhook")
async def webhook(request: Request):
    payload = await request.json()

    if payload.get('entity_type') == "discussion":
        message_id = payload.get('id')
    else:
        message_id = payload.get('thread').get('message_id')
    
    thread_id = pachkaDef.create_thread(message_id)

    # answer = "test"
    answer = await chunk.async_get_answer(query=payload.get('content').replace("/hello", "").replace("@нюра", "").strip())
    
    content = answer
    
    data_responce = pachkaDef.send_responce(thread_id, content)

    return {"status": "success"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.0", port=8080)

# ! Запустите сервер:
# ? uvicorn main:app --port 8080
