from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from pydantic import BaseModel
import datetime
import sqlite3
import pandas as pd

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
    "danielle": {
        "username": "danielle",
        "full_name": "danielle",
        "email": "danielle@example.com",
        "hashed_password": "fakehashedsecret3",
        "disabled": False,
    },
    "john": {
        "username": "john",
        "full_name": "john",
        "email": "john@example.com",
        "hashed_password": "fakehashedsecret4",
        "disabled": False,
    },
}

app = FastAPI()

def fake_hash_password(password: str):
    return "fakehashed" + password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

class UserInDB(User):
    hashed_password: str

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)
    return user

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user

@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}


@app.get("/get_task/{id}")
def get_task(id: int, current_user: Annotated[User, Depends(get_current_active_user)]):
    con = sqlite3.connect("./data.db")
    sel_task = pd.read_sql_query(
        f"SELECT * FROM completed_tasks WHERE id = {id}", 
        con, 
        parse_dates=['created_timestamp', 'override_date'],
    )
    return sel_task.iloc[0].to_dict()

@app.put("/put_task/")
def put_task(date: datetime.datetime, task_name: str, project_name: str):
    con = sqlite3.connect("./data.db")
    cursor = con.cursor()

    tmstp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(f"INSERT INTO completed_tasks \
        (created_timestamp,override_date,task_name,project_name) \
        VALUES ('{tmstp}','{date.date()}','{task_name}','{project_name}')")
    con.commit()
    cursor.close()
    con.close()

@app.get("/api/do_stuff/")
def do_stuff():
    with open("./out.txt", "w") as file:
        tmstp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"printed at: {tmstp}")

app.mount("/", StaticFiles(directory="static",html = True), name="static")