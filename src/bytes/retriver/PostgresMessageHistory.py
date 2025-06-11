from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from sqlalchemy.orm import Session
from bytes.database.models import ChatMemory

class PostgresMessageHistory(BaseChatMessageHistory):
    def __init__(self, db_manager: Session, thread_id: str) -> None:
        self._db_manager = db_manager
        self._thread_id = thread_id

    @property
    def messages(self) -> list[BaseMessage]:
        rows = (
            self._db_manager.query(ChatMemory)
            .filter(ChatMemory.thread_id == self._thread_id)
            .order_by(ChatMemory.created_at.asc())
            .all()
        )
        parsed: list[BaseMessage] = []
        for row in rows:
            if row.role == "user":
                parsed.append(HumanMessage(content=row.message_data))
            elif row.role == "ai":
                parsed.append(AIMessage(content=row.message_data))
        return parsed

    def add_messages(self, messages: list[BaseMessage]) -> None:
        for message in messages:
            if isinstance(message, HumanMessage):
                role = "user"
            elif isinstance(message, AIMessage):
                role = "ai"
            else:
                continue  # skip unsupported message types
            self._db_manager.add(ChatMemory(
                thread_id=self._thread_id,
                role=role,
                message_data=message.content
            ))
        self._db_manager.commit()

    def clear(self) -> None:
        self._db_manager.query(ChatMemory).filter(
            ChatMemory.thread_id == self._thread_id
        ).delete()
        self._db_manager.commit()
