from fastapi import FastAPI, Request, Depends, HTTPException, status, Response, Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

from typing import Annotated
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import sqlite3
import pandas as pd

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "85935d4cfcdbce5b38b823fa0f453be55a27e0fa863098d8f126f2aa88be874a"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": '$2b$12$RYQixhK.3ntjpSSeezp39O6I2drAhZXRsTFchrAtIL04uE3KNeXTS'
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": '$2b$12$XlwlFZbgd9Qo3UAl.DARK.4r8/7KbgA0TY53dFu5xV6FDDD5EojYC'
    },
    "danielle": {
        "username": "danielle",
        "full_name": "Danielle Migliozzi",
        "email": "danielle@example.com",
        "hashed_password": '$2b$12$OwatVfC6sT/ymYXfCsEOBeZoygeUwh.XQUZS4..k1bZwAGj1d32hK'
    },
    "john": {
        "username": "john",
        "full_name": "John Migliozzi",
        "email": "john@example.com",
        "hashed_password": '$2b$12$5lJ45GFbybzjvBz0UVc7PecSVFbjx2tg2y57Tf73blU3e/t5olccC'
    },
}

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None

class UserInDB(User):
    hashed_password: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(access_token: Annotated[str | None, Cookie()] = None):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response
):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES*60,
        httponly=True,
        secure=True,
        samesite="strict"
    )
    return True

@app.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return True


@app.get("/users/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user

@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]

@app.get("/get_task/{id}")
def get_task(id: int, current_user: Annotated[User, Depends(get_current_user)]):
# def get_task(id: int):
    con = sqlite3.connect("./data.db")
    sel_task = pd.read_sql_query(
        f"SELECT * FROM completed_tasks WHERE id = {id}", 
        con, 
        parse_dates=['created_timestamp', 'override_date'],
    )
    return sel_task.iloc[0].to_dict()

@app.put("/put_task/")
def put_task(date: datetime, task_name: str, project_name: str):
    con = sqlite3.connect("./data.db")
    cursor = con.cursor()

    tmstp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(f"INSERT INTO completed_tasks \
        (created_timestamp,override_date,task_name,project_name) \
        VALUES ('{tmstp}','{date.date()}','{task_name}','{project_name}')")
    con.commit()
    cursor.close()
    con.close()

@app.get("/api/do_stuff/")
def do_stuff():
    with open("./out.txt", "w") as file:
        tmstp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"printed at: {tmstp}")

app.mount("/", StaticFiles(directory="static",html = True), name="static")