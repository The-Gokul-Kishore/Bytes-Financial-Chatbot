from pydantic import BaseModel , EmailStr
from typing import Optional

class UserCreate(BaseModel):
    """user creationg request model
    """
    email:EmailStr
    password:str
    username:str
class UserOut(BaseModel):
    """ for outputting data and stuff like that

    Args:
        BaseModel (_type_): _description_
    """
    id: int
    email: EmailStr

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


class Query(BaseModel):
    query: str
    thread_id: int
    thread_specific_call: Optional[bool] = False