from bytes.database.crud.ClientManager import ClientManager
from bytes.database.crud.ThreadManager import ThreadManager
from bytes.database.models import Chat, Thread
from sqlalchemy.orm import Session


class ChatManager:
    def __init__(self):
        self.client_service = ClientManager()
        self.thread_service = ThreadManager()

    def create_chat_by_username(
        self, username: str, thread_id: int, content: str, db: Session
    ) -> Chat:
        client = self.client_service.get_client_by_username(username, db)
        if not client:
            raise ValueError(f"User '{username}' not found")
        thread = self.thread_service.get_thread_by_id(thread_id, db)
        if thread.client_id != client.client_id and client.username != "bot":
            raise ValueError(f"Thread {thread_id} does not belong to {username}")

        new_chat = Chat(content=content, sender_id=client.client_id, chat_id=thread_id)
        db.add(new_chat)
        db.flush()
        db.refresh(new_chat)
        return new_chat

    def get_chats_by_thread_username(
        self, username: str, thread_id: int, db: Session
    ) -> list[Chat]:
        
        client = self.client_service.get_client_by_username(username, db)
        if not client:
            raise ValueError(f"User '{username}' not found")
        user_id_of_thread = (
            db.query(Thread).filter(Thread.thread_id == thread_id).first().client_id
        )
        if user_id_of_thread != client.client_id:
            raise ValueError(f"Thread {thread_id} does not belong to {username}")
        return (
            db.query(Chat)
            .filter(Chat.chat_id == thread_id, Chat.sender_id == client.client_id)
            .all()
        )

    def get_chats_by_thread(self, thread_id: int, db: Session) -> list[Chat]:
        return db.query(Chat).filter(Chat.chat_id == thread_id).all()
