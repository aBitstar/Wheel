from typing import List
from pydantic import EmailStr
from sqlalchemy import CheckConstraint
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    status: str | None = Field(default=None, max_length=255)

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner")
    status: str | None = Field(default=None, max_length=255)
    sent_requests: List["FriendRequest"] = Relationship(back_populates="sender", sa_relationship_kwargs={"foreign_keys": "[FriendRequest.sender_id]"})
    received_requests: List["FriendRequest"] = Relationship(back_populates="receiver", sa_relationship_kwargs={"foreign_keys": "[FriendRequest.receiver_id]"})
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow},)

# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: int


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    title: str = Field(min_length=1, max_length=255)


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=255)
    owner_id: int | None = Field(default=None, foreign_key="user.id", nullable=False)
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: int
    owner_id: int


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: int | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


# Friend Request
class FriendRequestBase(SQLModel):
    sender_id: int
    receiver_id: int


class FriendRequest(FriendRequestBase, table=True):
    id: int = Field(default=None, primary_key=True, index=True)
    sender_id: int = Field(foreign_key="user.id")
    receiver_id: int = Field(foreign_key="user.id")
    status: str = Field(enumerate(['accepted', 'rejected', 'pending']))
    sender: User = Relationship(back_populates="sent_requests", sa_relationship_kwargs={"foreign_keys": "[FriendRequest.sender_id]"})
    receiver: User = Relationship(back_populates="received_requests", sa_relationship_kwargs={"foreign_keys": "[FriendRequest.receiver_id]"})
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow},)

class FriendBase(SQLModel):
    user1: int
    user2: int

class Friend(FriendBase, table=True):
    id: int = Field(default=None, primary_key=True, index=True)
    user1: int = Field(foreign_key="user.id")
    user2: int = Field(foreign_key="user.id")
    friends_since: datetime = Field(default_factory=datetime.utcnow)
    __table_args__ = (CheckConstraint('user1 < user2', name='check_user1_less_than_user2'),)

class RequestSent(SQLModel):
    sender_id: int
    receiver_id: int