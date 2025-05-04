from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
import datetime
import sqlite3
import pandas as pd

app = FastAPI()

@app.get("/get_task/{id}")
def get_task(id: int):
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