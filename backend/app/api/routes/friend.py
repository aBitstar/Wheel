from ast import alias
from typing import List, Tuple
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.orm import aliased

from app.api.deps import CurrentUser, SessionDep
from app.models import AcceptRequest, Friend, FriendPublic, FriendRequest, FriendRequestPublic, RequestSent, User, UsersPublic
from app.websocket.websocket import accept_friend, decline_friend, send_Request

router = APIRouter()

friend_requests = {}
friend_accepts = {}

@router.post('/send-request', response_model=FriendRequest)
async def send_request(request: RequestSent, session: SessionDep, currentUser: CurrentUser):
    """
    Send Friend Request
    Send friend request to a user and returns the request.
    """

    if currentUser.id == request.receiver_id:
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
    existing_friends = session.exec(select(Friend).where(Friend.user1 == user1, Friend.user2 == user2)).first()
    print(existing_friends, ' ')
    if existing_friends:
        raise HTTPException(status_code=400, detail="You are already friends!")

    # Check if the request exists
    existing_request = session.exec(select(FriendRequest).where(
        FriendRequest.sender_id == request.sender_id,
        FriendRequest.receiver_id == request.receiver_id,
        FriendRequest.status == 'pending'
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
    await send_Request(request.receiver_id, f"New friend request from {sender.full_name}")
    return friend_request

@router.post('/accept-request', response_model=list[FriendRequestPublic])
async def accept_request(request: AcceptRequest, session: SessionDep, currentUser: CurrentUser):
    """
    Accept a friend request
    Accept a friend request, notify the request sender and returns updated requests list.
    """

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
    existing_friends = session.exec(select(Friend).where(Friend.user1 == user1, Friend.user2 == user2)).first()
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


@router.post('/decline-request', response_model=list[FriendRequestPublic])
async def decline_request(request: AcceptRequest, session: SessionDep, currentUser: CurrentUser):
    """
    Decline a friend request
    Decline a friend request, notify the request sender and returns updated requests list.
    """

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

@router.get('/requests-me', response_model=list[FriendRequestPublic])
def get_requests_to_me(session: SessionDep, currentUser: CurrentUser):
    """
    Retrieve all freind requests sent to the current user.
    Returns a list of all friend requests with names and emails of request senders.
    """

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

@router.get('/myfriends', response_model=list[FriendPublic])
def get_all_my_friends(session: SessionDep, currentUser: CurrentUser):
    """
    Retrieve all accepted friends of current user.
    Returns a list of all friends with their names, emails and the dates of accepting friend requests.
    """

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
        friend: FriendPublic = {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "status": user.status,
            "friends_since": friend.friends_since
        }
        friend_list.append(friend)
    return friend_list