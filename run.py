from cmath import log
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import random
import json
import uvicorn
import os

from process_data import process

# Create application
app = FastAPI(title='WebSocket Example')

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        for connection in self.active_connections:
            print(connection)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, data: dict):
        for connection in self.active_connections:
            await connection.send_json(json.dumps(data))

manager = ConnectionManager()


@app.get('/')
async def root():
    return {"message": "Hello World"}

# @app.websocket("/ws/{client_id}")
# async def websocket_endpoint(websocket: WebSocket, client_id: int):
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Open websocket
    await manager.connect(websocket)

    try:
        # Until forever do the following...
        while True:
            data = await websocket.receive_json()
            print(f'received data! it is\n{data}')
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            process(data)
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")

if __name__=="__main__":
    uvicorn.run("run:app", host="0.0.0.0", port=os.getenv("PORT", default=5002),log_level="info")
