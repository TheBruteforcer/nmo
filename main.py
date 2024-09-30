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
async def add_post(r: Request, conn=Depends(get_db)):
    data = await r.json()
    ref = conn.cursor()
    
    # Get the maximum id from the POSTS table
    ref.execute("SELECT MAX(id) FROM POSTS")
    result = ref.fetchone()
    new_id = result[0] + 1 if result[0] is not None else 1  # Set id to 1 if no posts exist
    
    # Insert the new post
    ref.execute(
        "INSERT INTO POSTS (id, type, title, desc, html) VALUES (?, ?, ?, ?, ?)",
        (new_id, data["type"], data["title"], data["desc"], data["html"])
    )
    
    conn.commit()  # Commit the transaction
    ref.close()  # Close the cursor
    
    return {"success": True}

    
