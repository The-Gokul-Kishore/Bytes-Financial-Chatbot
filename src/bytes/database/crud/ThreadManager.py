from bytes.database.crud.ClientManager import ClientManager
from bytes.database.models import Thread
from sqlalchemy.orm import Session


class ThreadManager:
    def __init__(self):
        self.client_service = ClientManager()

    def create_thread_by_username(
        self, username: str, thread_type: str, db: Session
    ) -> Thread:
        client = self.client_service.get_client_by_username(username, db)
        if not client:
            raise ValueError(f"User '{username}' not found")

        new_thread = Thread(
            client_id=client.client_id,
            thread_type=thread_type,
            thread_name=f"Thread-{thread_type}",
        )
        db.add(new_thread)
        db.flush()
        db.refresh(new_thread)

        new_thread.thread_name = f"chat-{new_thread.thread_id}"
        db.flush()
        db.refresh(new_thread)
        return new_thread

    def get_threads_by_username(self, username: str, db: Session) -> list[Thread]:
        client = self.client_service.get_client_by_username(username, db)
        if not client:
            raise ValueError(f"User '{username}' not found")
        return db.query(Thread).filter(Thread.client_id == client.client_id).all()

    def delete_thread_by_username(
        self, username: str, thread_id: int, db: Session
    ) -> None:
        client = self.client_service.get_client_by_username(username, db)
        if not client:
            raise ValueError(f"User '{username}' not found")
        db.query(Thread).filter(
            Thread.thread_id == thread_id, Thread.client_id == client.client_id
        ).delete()
        db.flush()

    def get_thread_by_id(self, thread_id: int, db: Session) -> Thread:
        return db.query(Thread).filter(Thread.thread_id == thread_id).first()
