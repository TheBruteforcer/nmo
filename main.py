from fastapi import FastAPI, Query, Request, Depends, HTTPException
from sqlite3 import connect, Connection
from fastapi.middleware.cors import CORSMiddleware

# Initialize the FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins; change this to your frontend's origin in production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


# Database connection handler
def get_db():
    conn = connect("app.db", check_same_thread=False)  # Disable thread check
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
        print(f"Error creating table: {e}")
    try:
        yield conn
    finally:
        conn.close()
# Get all posts
@app.get("/get-posts")
def all_posts(conn: Connection = Depends(get_db)):
    resp = []
    ref = conn.cursor()
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return resp

# Get a specific post by ID
@app.get("/get-post")
def post(id: int = Query(...), conn: Connection = Depends(get_db)):
    ref = conn.cursor()
    try:
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
            raise HTTPException(status_code=404, detail="Post not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add a new post
@app.post("/add-post")
async def add_post(r: Request, conn: Connection = Depends(get_db)):
    try:
        data = await r.json()
        
        # Ensure all expected keys are present in the incoming JSON
        required_fields = ["type", "title", "desc", "html"]
        for field in required_fields:
            if field not in data:
                raise HTTPException(status_code=400, detail=f"Missing field: {field}")
        
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
