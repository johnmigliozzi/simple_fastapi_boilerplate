from fastapi import FastAPI, Request, Depends, HTTPException, status, Response, Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from typing import Annotated
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import os
import sqlite3
import pandas as pd

SECRET_KEY = os.getenv("SECRET_KEY", "dev_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "11520"))
COOKIE_SECURE = os.getenv("COOKIE_SECURE") == "true"

users_list = {
    "admin": {
        "username": "admin",
        "full_name": "Admin",
        "hashed_password": '$argon2id$v=19$m=65536,t=3,p=4$lrZ2xZm9mArqMd0sCS3Dyw$ZwGuTqGsy8jPeE5PXN20iIe/Q+IoQXnUn3nAz6l+owI'
    }
}

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str
    full_name: str | None = None

class UserInDB(User):
    hashed_password: str

password_hash = PasswordHash.recommended()

app = FastAPI()

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_hash.hash(password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
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
    user = get_user(users_list, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response
):
    user = authenticate_user(users_list, form_data.username, form_data.password)
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
        secure=COOKIE_SECURE,
        samesite="strict"
    )
    return True

@app.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return True

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user

@app.get("/get_task/{id}")
def get_task(id: int, current_user: Annotated[User, Depends(get_current_user)]):
    con = sqlite3.connect("./data.db")
    sel_task = pd.read_sql_query(
        f"SELECT * FROM completed_tasks WHERE id = {id}", 
        con, 
        parse_dates=['created_timestamp', 'override_date'],
    )
    return sel_task.iloc[0].to_dict()

app.mount("/", StaticFiles(directory="static",html = True), name="static")