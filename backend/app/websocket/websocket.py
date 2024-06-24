from fastapi import WebSocket, WebSocketDisconnect
from typing import List

active_connections: List[WebSocket] = []

async def connect(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)

def disconnect(websocket: WebSocket):
    active_connections.remove(websocket)

async def broadcast_message(message: str):
    for connection in active_connections:
        await connection.send_text(message)

async def websocket_endpoint(websocket: WebSocket):
    await connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Process incoming messages here if needed
    except WebSocketDisconnect:
        disconnect(websocket)
