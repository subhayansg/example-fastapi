from random import randrange
import time
from typing import Optional
from fastapi import FastAPI, HTTPException, status, Response
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

class Post(BaseModel):
    title: str                      # mandatory
    content: str                    # mandatory
    published: bool = True          # if not provided, will default to True
    # rating: Optional[int] = None    # Completely optional

while True:
    try:
        conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='poly40sg', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successful!")
        break
    except Exception as error:
        print("Connection to database has failed!")
        print("Error: ", error)
        time.sleep(2)

my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1},
{"title": "title of post 2", "content": "content of post 2", "id": 2}]

def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p

def find_post_index(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i

# ("/") is the root path --> http://127.0.0.1:8000
@app.get("/")
async def root():
    return{"message": "Hello World!!"}

# go to --> http://127.0.0.1:8000/posts
@app.get("/posts")
def get_posts():
    # return {"message", "These are all posts!"}
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    return {"message": posts}

# go to --> http://127.0.0.1:8000/posts
# from postman add POST, Body - raw, JSON
'''
@app.post("/posts")
def create_posts(payload: dict = Body(...)):
    # payload: dict = Body(...) --> it will extract all the fields from the payload and load it into a dictionary called payload
    return {f"new_post": f"title: {payload['title']}, content: {payload['content']}"}
'''
@app.post("/posts", status_code=status.HTTP_201_CREATED)  # to update the default status_code
def create_posts(new_post: Post):
    # we are validating if the contents of post is as per Post (it has a title and content of type str or atleast of a type that can be casted to str)
    # print(new_post.title)
    # print(new_post.content)
    # print(new_post.published)
    # print(new_post.rating)
    new_updated_post = new_post.dict() # pydantic model has a function dict() which converts the object to dict type
    new_updated_post["id"] = randrange(0, 1000000)
    my_posts.append(new_updated_post)
    return {"data": new_updated_post}

# Get a specific post
# go to --> http://127.0.0.1:8000/posts/2 for example
@app.get("/posts/{id}")   # id is called "path parameter"
def get_post(id: int):    # whatever we pass from decorator above is available to the function; id, make sure id passed in from postman is int
                          # i.e. if http://127.0.0.1:8000/posts/bababa is passed, it'll through a meaningfull error
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post {id} was not found!!!")
    return {"post_detail": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    index = find_post_index(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found!!!")
    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    index = find_post_index(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The post {id} was not found!!!")
    post_dict = post.dict()
    # print(post_dict)
    my_posts[index] = post_dict
    return {"data": post_dict}
