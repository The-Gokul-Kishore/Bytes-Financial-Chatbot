from sqlalchemy.orm import declarative_base
from datetime import datetime

from sqlalchemy import (
    TIMESTAMP,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class DocStore(Base):
    __tablename__ = "docstore"
    doc_id = Column(String, primary_key=True)
    content = Column(Text, nullable=False)
class Clients(Base):
    __tablename__ = "Clients"
    client_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    threads = relationship("Thread", back_populates="owner")
    hashed_password = Column(String, nullable=False)
    chats = relationship("Chat", back_populates="sender", cascade="all, delete")


class Thread(Base):
    __tablename__ = "Thread"
    thread_id = Column(Integer, primary_key=True, index=True)
    client_id = Column(
        Integer, ForeignKey("Clients.client_id", ondelete="CASCADE"), nullable=False
    )
    thread_name = Column(String, nullable=False)
    thread_type = Column(String, nullable=False)
    created_at = Column(
        DateTime, default=datetime.utcnow, nullable=False
    )  # Add DateTime column with default value
    owner = relationship("Clients", back_populates="threads")
    chats = relationship("Chat", back_populates="thread", cascade="all, delete")



class Chat(Base):
    __tablename__ = "Chat"
    message_id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(
        Integer, ForeignKey("Thread.thread_id", ondelete="CASCADE"), nullable=False
    )
    sender_id = Column(
        Integer, ForeignKey("Clients.client_id", ondelete="CASCADE"), nullable=False
    )
    content = Column(Text, nullable=False)
    sent_at = Column(TIMESTAMP, server_default=func.now())
    thread = relationship("Thread", back_populates="chats")
    sender = relationship("Clients", back_populates="chats")


class ChatMemory(Base):
    __tablename__ = "chat_memory"
    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(Integer, ForeignKey("Thread.thread_id", ondelete="CASCADE"), nullable=False)
    message_data = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
