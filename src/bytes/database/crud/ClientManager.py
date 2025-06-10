from bytes.database.models import Clients
from sqlalchemy.orm import Session


class ClientManager:
    def create_client(
        self, email: str, password: str, username: str, db: Session
    ) -> Clients:
        #will has in future
        hashed_pw = password
        new_client = Clients(email=email, username=username, hashed_password=hashed_pw)
        db.add(new_client)
        db.flush()
        db.refresh(new_client)
        return new_client

    def get_client_by_id(self, client_id: int, db: Session) -> Clients | None:
        return db.query(Clients).filter(Clients.client_id == client_id).first()

    def get_client_by_username(self, username: str, db: Session) -> Clients | None:
        return db.query(Clients).filter(Clients.username == username).first()

    def delete_client_by_id(self, client_id: int, db: Session) -> None:
        db.query(Clients).filter(Clients.client_id == client_id).delete()
        db.flush()
