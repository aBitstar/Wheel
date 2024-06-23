import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import FriendRequest, User

router = APIRouter()

@router.post('/send-request')
def sendRequest(sender_id: int, receiver_id: int, session: SessionDep):
    if sender_id == receiver_id:
        raise HTTPException(status_code=400, detail="You can't send request to yourself")
    # Check if sender or receiver exists
    from_user = session.get(User, sender_id)
    to_user = session.get(User, receiver_id)

    if not from_user or not to_user:
        raise HTTPException(status_code=404, detail="User not found")
    # Check if the request exists
    existing_request = session.exec(select(FriendRequest).where(
        FriendRequest.sender_id == sender_id,
        FriendRequest.receiver_id == receiver_id
    )).first()
    if existing_request:
        raise HTTPException(status_code=400, detail="Friend request already sent")
    
    friend_request = FriendRequest(sender_id=sender_id, receiver_id=receiver_id, status="pending")
    session.add(friend_request)
    session.commit()
    session.refresh(friend_request)
    return friend_request

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