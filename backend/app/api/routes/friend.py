from ast import alias
from typing import List, Tuple
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.orm import aliased

from app.api.deps import CurrentUser, SessionDep
from app.models import AcceptRequest, Friend, FriendRequest, RequestSent, User
from app.websocket.websocket import accept_friend, broadcast_message, decline_friend, send_request

router = APIRouter()

friend_requests = {}
friend_accepts = {}

@router.post('/send-request')
async def send_request(request: RequestSent, session: SessionDep):
    if request.sender_id == request.receiver_id:
        raise HTTPException(status_code=400, detail="You can't send request to yourself")
    # Check if sender or receiver exists
    from_user = session.get(User, request.sender_id)
    to_user = session.get(User, request.receiver_id)

    if not from_user or not to_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if friend relationship exists
    if request.sender_id > request.receiver_id:
        user1 = request.receiver_id
        user2 = request.sender_id
    else:
        user1 = request.sender_id
        user2 = request.receiver_id
    existing_friends = session.exec(select(Friend).where(Friend.user1 == user1, Friend.user2 == user2))
    if existing_friends:
        raise HTTPException(status_code=400, detail="You are already friends!")

    # Check if the request exists
    existing_request = session.exec(select(FriendRequest).where(
        FriendRequest.sender_id == request.sender_id,
        FriendRequest.receiver_id == request.receiver_id
    )).first()
    if existing_request:
        raise HTTPException(status_code=400, detail="Friend request already sent")
    friend_request = FriendRequest(sender_id=request.sender_id, receiver_id=request.receiver_id, status="pending")
    session.add(friend_request)
    session.commit()
    session.refresh(friend_request)
    # sending the request
    sender = session.exec(select(User).where(User.id == request.sender_id)).first()
    friend_requests[request.receiver_id] = request.sender_id
    await send_request(request.receiver_id, f"New friend request from {sender.full_name}")
    return friend_request

@router.post('/accept-request')
async def accept_request(request: AcceptRequest, session: SessionDep, currentUser: CurrentUser):
    existing_request = session.exec(select(FriendRequest).where(
        FriendRequest.sender_id == request.sender_id,
        FriendRequest.receiver_id == request.receiver_id,
        FriendRequest.status == "pending"
    )).first()
    if not existing_request:
        raise HTTPException(status_code=404, detail="Friend request not found or already accepted")
    
    if request.sender_id > request.receiver_id:
        user1 = request.receiver_id
        user2 = request.sender_id
    else:
        user1 = request.sender_id
        user2 = request.receiver_id
    existing_friends = session.exec(select(Friend).where(Friend.user1 == user1, Friend.user2 == user2))
    if existing_friends:
        raise HTTPException(status_code=400, detail="You are already friends!")

    # Update the status of the friend request to 'accepted'
    existing_request.status = "accepted"
    session.add(existing_request)
    session.commit()
    session.refresh(existing_request)

    # Add friend relationship
    friends = Friend(user1 = user1, user2 = user2)
    session.add(friends)
    session.commit()
    session.refresh(friends)
    #sending accepts
    receiver = session.get(User, request.receiver_id)
    friend_accepts[request.receiver_id] = request.sender_id
    await accept_friend(request.sender_id, f"{receiver.full_name} accepted your friend request!")
    results = session.exec(select(FriendRequest, User).join(User, User.id == FriendRequest.sender_id)
    .where(
        FriendRequest.receiver_id == currentUser.id,
        FriendRequest.status == "pending"
    )).all()
    requests = []
    for friend_request, sender_user in results:
        request_dict = {
            "id": friend_request.id,
            "sender_id": friend_request.sender_id,
            "receiver_id": friend_request.receiver_id,
            "status": friend_request.status,
            "sender_name": sender_user.full_name,  
            "sender_email": sender_user.email
        }
        requests.append(request_dict)
    return requests


@router.post('/decline-request')
async def decline_request(request: AcceptRequest, session: SessionDep, currentUser: CurrentUser):
    existing_request = session.exec(select(FriendRequest).where(
        FriendRequest.sender_id == request.sender_id,
        FriendRequest.receiver_id == request.receiver_id,
        FriendRequest.status == "pending"
    )).first()
    if not existing_request:
        raise HTTPException(status_code=404, detail="Friend request not found or already accepted")

    # Update the status of the friend request to 'declined'
    existing_request.status = "declined"
    session.add(existing_request)
    session.commit()
    session.refresh(existing_request)

    #sending accepts
    receiver = session.get(User, request.receiver_id)
    friend_accepts[request.receiver_id] = request.sender_id
    await decline_friend(request.sender_id, f"{receiver.full_name} declined your friend request!")
    results = session.exec(select(FriendRequest, User).join(User, User.id == FriendRequest.sender_id)
    .where(
        FriendRequest.receiver_id == currentUser.id,
        FriendRequest.status == "pending"
    )).all()
    requests = []
    for friend_request, sender_user in results:
        request_dict = {
            "id": friend_request.id,
            "sender_id": friend_request.sender_id,
            "receiver_id": friend_request.receiver_id,
            "status": friend_request.status,
            "sender_name": sender_user.full_name,  
            "sender_email": sender_user.email
        }
        requests.append(request_dict)
    return requests

@router.get('/requests-me')
def get_requests_to_me(session: SessionDep, currentUser: CurrentUser):
    results = session.exec(select(FriendRequest, User).join(User, User.id == FriendRequest.sender_id)
    .where(
        FriendRequest.receiver_id == currentUser.id,
        FriendRequest.status == "pending"
    )).all()
    requests = []
    for friend_request, sender_user in results:
        request_dict = {
            "id": friend_request.id,
            "sender_id": friend_request.sender_id,
            "receiver_id": friend_request.receiver_id,
            "status": friend_request.status,
            "sender_name": sender_user.full_name,  
            "sender_email": sender_user.email
        }
        requests.append(request_dict)
    return requests

@router.get('/myfriends')
def get_all_my_friends(session: SessionDep, currentUser: CurrentUser):
    friends1 = session.exec(select(Friend, User)
                            .join(Friend, Friend.user2 == User.id)
                            .where(Friend.user1 == currentUser.id)).all()
    friends2 = session.exec(select(Friend, User)
                            .join(Friend, Friend.user1 == User.id)
                            .where(Friend.user2 == currentUser.id)).all()
    friends: List[Tuple[Friend, User]] = friends1 + friends2
    print(friends, ' ')
    friend_list = []
    for friend, user in friends:
        friend = {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "status": user.status,
            "friends_since": friend.friends_since
        }
        friend_list.append(friend)
    return friend_list