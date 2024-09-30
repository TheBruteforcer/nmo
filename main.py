from fastapi import FastAPI, Query, Request, Depends
from sqlite3 import connect, Connection

app = FastAPI()

# Database dependency
def get_db():
    conn = connect("app.db")
    try:
        conn.cursor().execute("""
            CREATE TABLE IF NOT EXISTS POSTS (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                TYPE TEXT,
                TITLE TEXT,
                DESC TEXT,
                HTML TEXT
            )
        """)
    except Exception as e:
        print(f"Error: {e}")
    try:
        yield conn
    finally:
        conn.close()

# Get all posts
@app.get("/get-posts")
def all_posts(conn: Connection = Depends(get_db)):
    resp = []
    ref = conn.cursor()
    ref.execute("SELECT * FROM POSTS")
    posts = ref.fetchall()
    for post in posts:
        resp.append({
            "id": post[0],
            "type": post[1],
            "title": post[2],
            "desc": post[3],
            "html": post[4]
        })
    return resp

# Get a specific post by ID
@app.get("/get-post")
def post(id: int = Query(...), conn: Connection = Depends(get_db)):
    ref = conn.cursor()
    ref.execute("SELECT * FROM POSTS WHERE ID = ?", (id,))
    post = ref.fetchone()
    
    if post:
        return {
            "id": post[0],
            "type": post[1],
            "title": post[2],
            "desc": post[3],
            "html": post[4]
        }
    else:
        return {"error": "Post not found"}

# Add a new post
@app.post("/add-post")
async def add_post(r: Request, conn: Connection = Depends(get_db)):
    data = await r.json()
    ref = conn.cursor()
    
    # Insert the new post
    ref.execute(
        "INSERT INTO POSTS (type, title, desc, html) VALUES (?, ?, ?, ?)",
        (data["type"], data["title"], data["desc"], data["html"])
    )
    
    conn.commit()  # Commit the transaction
    new_id = ref.lastrowid  # Get the ID of the newly inserted post
    ref.close()  # Close the cursor
    
    return {"success": True, "new_id": new_id}
