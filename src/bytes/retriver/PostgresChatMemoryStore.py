from bytes.database.models import ChatMemory
from langchain_core.memory import BaseMemory
from pydantic import PrivateAttr
from sqlalchemy.orm import Session


class PostgresChatMemoryStore(BaseMemory):
    _db_manager: Session = PrivateAttr()
    _thread_id: int = PrivateAttr()

    def __init__(self, db_manager: Session, thread_id: int):
        self._db_manager = db_manager
        self._thread_id = thread_id

    def load_memory_variables(self, inputs: dict) -> dict:
        messages = (
            self._db_manager.query(ChatMemory)
            .filter(ChatMemory.thread_id == self._thread_id)
            .order_by(ChatMemory.created_at.asc())
            .all()
        )
        history = [msg.message_data for msg in messages]
        return {"history": "\n".join(history)}

    def save_context(self, inputs: dict, outputs: dict) -> None:
        new_memory = ChatMemory(
            thread_id=self._thread_id,
            message_data=f"User: {inputs['input']}\nBot: {outputs['output']}",
        )
        self._db_manager.add(new_memory)
        self._db_manager.commit()

    @property
    def memory_variables(self) -> list[str]:
        return ["history"]

    def clear(self) -> None:
        self._db_manager.query(ChatMemory).filter(
            ChatMemory._thread_id == self._thread_id
        ).delete()
        self._db_manager.commit()
