from fastapi import FastAPI, Query, Request, Depends
from json import dumps, loads
from sqlite3 import *

def get_db():
    conn = connect("app.db")
    try:
        conn.cursor().execute("CREATE TABLE POSTS (ID TEXT,TYPE TEXT, TITLE TEXT, DESC TEXT, HTML TEXT)")
    except:
        pass
    yield conn

app = FastAPI()

@app.get("/get-posts")
def all_posts(conn = Depends(get_db)):
    resp = []
    ref = conn.cursor()
    ref.execute("SELECT * FROM POSTS")
    posts = ref.fetchall()
    for post in posts :
        resp.append({"id" : post[0], "type" : post[1], 'title' : post[2], "desc" : post[3], "pares" : post[4] })
        
    return resp

@app.get("/get-post")
def post(id : str = Query(...), conn = Depends(get_db)):
    resp = []
    ref = conn.cursor()
    ref.execute("SELECT * FROM POSTS WHERE ID = ?", (id,))
    posts = ref.fetchall()
    for post in posts :
        resp.append({"id" : post[0], "type" : post[1], 'title' : post[2], "desc" : post[3], "pares" : post[4] })

        
    return resp

@app.post("/add-post")
async def add(r : Request, conn = Depends(get_db)):
   data = await r.json()
   ref = conn.cursor()
   ref.execute("SELECT * FROM POSTS")
   id = 0
   for p in ref.fetchall():
       id += int(p[0])
   ref.execute("INSERT INTO POSTS (?, ?, ?, ? ,?)", (str(id), data["type"], data["title"], data["desc"], data["html"]))
   return {"success" : True}
   
    
