from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict

active_connections: Dict[int, WebSocket] = {}

async def connect(websocket: WebSocket, user_id: int):
    await websocket.accept()
    active_connections[user_id] = websocket
    

def disconnect(user_id: int):
    active_connections.pop(user_id, None)

async def broadcast_message(message: str):
    for connection in active_connections.values():
        await connection.send_text(message)

async def broadcast_to_friends(friends: list, message: str):
    for friend_id in friends:
        await send_Request(friend_id, message)

async def send_Request(receiver_id: int, message: str):
    if receiver_id in active_connections:
        await active_connections[receiver_id].send_text(message)

async def accept_friend(sender_id: int, message: str):
    if sender_id in active_connections:
        await active_connections[sender_id].send_text(message)

async def decline_friend(sender_id: int, message: str):
    if sender_id in active_connections:
        await active_connections[sender_id].send_text(message)


async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Process incoming messages here if needed
    except WebSocketDisconnect:
        disconnect(user_id)
