from datetime import datetime, timedelta

from bytes.database import crud
from bytes.schemas import TokenData
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Authenticator:
    def __init__(
        self, SECRET_KEY: str, ALGORITHM: str, ACCESS_TOKEN_EXPIRE_MINUTES: int
    ):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.token_expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def authenticate_user(self, username: str, password: str, db: Session) -> dict:
        user = crud.ClientManager().get_client_by_username(username, db)
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return user

    def create_acess_token(self, username: str) -> str:
        expire = datetime.utcnow() + self.token_expire
        to_encode = {"sub": username, "exp": expire}

        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str = Depends(oauth2_scheme)) -> TokenData:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
            return token_data
        except JWTError:
            raise credentials_exception

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)
