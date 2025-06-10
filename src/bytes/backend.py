import os
from logging import getLogger
from bytes.agent_services.agent import Agent_Service
import uvicorn
from bytes.authenticator_service import Authenticator
from bytes.database import crud
from bytes.database.db import DBManager
from bytes.schemas import Query, Token, TokenData, UserCreate
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import json
logger = getLogger("uvicorn.error")
app = FastAPI()
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
auth_service = Authenticator(
    SECRET_KEY=os.getenv("SECRET_KEY", "secret_key"),
    ALGORITHM=os.getenv("ALGORITHM", "HS256"),
    ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "100")),
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter(dependencies=[Depends(auth_service.verify_token)])


def get_db_manager():
    """
    Returns a singleton instance of the DBManager class.

    Returns:
        DBManager: instance of the DBManager class
    """
    return DBManager()


def get_auth_service():
    return Authenticator(
        SECRET_KEY=os.getenv("SECRET_KEY", "secret_key"),
        ALGORITHM=os.getenv("ALGORITHM", "HS256"),
        ACCESS_TOKEN_EXPIRE_MINUTES=int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "100")
        ),
    )


def get_db_session(db_manager: DBManager = Depends(get_db_manager)):
    with db_manager.session() as session:
        yield session


@app.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db_session: Session = Depends(get_db_session),
    auth_service: Authenticator = Depends(get_auth_service),
):
    if form_data.username is None or form_data.password is None:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
        )

    user = auth_service.authenticate_user(
        form_data.username, form_data.password, db=db_session
    )
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
        )
    token = auth_service.create_acess_token(user.username)
    return Token(access_token=token, token_type="bearer")


@app.get("/verify-token")
async def verify_token_route(token: str = Depends(oauth2_scheme)):
    """
    Verifies whether a JWT token is valid.
    """
    try:
        tokendata = auth_service.verify_token(token)
        return {"valid": True, "username": tokendata.username}
    except HTTPException as e:
        raise e


@app.post("/create-user")
async def create_user(
    usercreate: UserCreate,
    db_session: Session = Depends(get_db_session),
    auth_service: Authenticator = Depends(get_auth_service),
):
    try:
        user = crud.ClientManager().create_client(
            username=usercreate.username,
            email=usercreate.email,
            password=usercreate.password,
            auth_service=auth_service,
            db=db_session,
        )
        return {
            "username": user.username,
            "email": user.email,
            "user_id": user.client_id,
        }
    except Exception as e:
        logger.error(f"Exception: {e}")
        raise HTTPException(status_code=400, detail=e)


@router.post("/query")
async def query(
    query: Query,
    session: Session = Depends(get_db_session),
    userToken: TokenData = Depends(auth_service.verify_token),
):
    try:
        if (
            crud.ThreadManager()
            .get_thread_by_id(thread_id=query.thread_id, db=session)
            .client_id
            != crud.ClientManager()
            .get_client_by_username(username=userToken.username, db=session)
            .client_id
        ):
            raise HTTPException(
                status_code=400, detail="Thread does not belong to user"
            )
        agent= Agent_Service(model="gemini-1.5-flash",db_manager=session)
        agent_response = agent.run_agent(query.query,thread_id=query.thread_id,db=session)
        chatmanager = crud.ChatManager()
        chatmanager.create_chat_by_username(
            username=userToken.username,
            thread_id=query.thread_id,
            content=query.query,
            db=session,
        )
        bot_response = chatmanager.create_chat_by_username(
            username="bot",
            thread_id=query.thread_id,
            content=json.dumps(agent_response),
            db=session,
        )
        return {
            "query": query.query,
            "response": agent_response["text_explanation"],
            "chart": agent_response["chart_json"],
            "table": agent_response["table_json"],
            "message_id": bot_response.chat_id,
        }
    except Exception as e:
        session.rollback()
        print("Exception:", e)


@router.get("/threads")
async def get_threads(
    db_session: Session = Depends(get_db_session),
    userToken: TokenData = Depends(auth_service.verify_token),
):
    try:
        thread_manager = crud.ThreadManager()
        threads = thread_manager.get_threads_by_username(
            username=userToken.username, db=db_session
        )
        return threads
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)


@router.get("/chats")
async def get_chats(
    thread_id: int,
    db_session: Session = Depends(get_db_session),
    usertoken: TokenData = Depends(auth_service.verify_token),
):
    try:
        if (
            crud.ThreadManager()
            .get_thread_by_id(thread_id=thread_id, db=db_session)
            .client_id
            != crud.ClientManager()
            .get_client_by_username(username=usertoken.username, db=db_session)
            .client_id
        ):
            raise HTTPException(
                status_code=400, detail="Thread does not belong to user"
            )
        chat_manager = crud.ChatManager()

        chats = chat_manager.get_chats_by_thread(thread_id=thread_id, db=db_session)
        return chats
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)


@router.post("/create-thread")
async def create_thread(
    thread_type: str,
    db_session: Session = Depends(get_db_session),
    usertoken: TokenData = Depends(auth_service.verify_token),
):
    thread_manager = crud.ThreadManager()
    thread = thread_manager.create_thread_by_username(
        username=usertoken.username, thread_type=thread_type, db=db_session
    )
    return thread


app.include_router(router=router)


def run_backend(port=8021, reload=True):
    uvicorn.run(
        "bytes.backend:app",
        host="127.0.0.1",
        port=port,
        reload=reload,
        workers=1,
    )


if __name__ == "__main__":
    try:
        run_backend()
    except Exception as e:
        print("application terminated with error:", e)
        raise
