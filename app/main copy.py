from pyexpat import model
from random import randrange
from signal import raise_signal
import time
from turtle import title
from typing import List, Optional
from fastapi import Depends, FastAPI, HTTPException, status, Response, Depends
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlalchemy
# ORM/sqlalchemy related
from . import models, schemas, utils
from app.database import SessionLocal, engine, get_db
from sqlalchemy.orm import Session

app = FastAPI()

models.Base.metadata.create_all(bind=engine)



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

@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data": posts}

# go to --> http://127.0.0.1:8000/posts
@app.get("/posts", response_model = List[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts

# go to --> http://127.0.0.1:8000/posts
# from postman add POST, Body - raw, JSON
@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model= schemas.Post)  # to update the default status_code, to use response class
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    #====================================== OLD PROCESS
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, 
    #                 (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    #======================================
    # new_post = models.Post(title=post.title, content=post.content, published=post.published)
    # instead of the above, typing out all columns, we can use Post.dict() method and unpack that dict
    new_post = models.Post(**post.dict())

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

# Get a specific post
# go to --> http://127.0.0.1:8000/posts/2 for example
@app.get("/posts/{id}", response_model=schemas.Post)   # id is called "path parameter"
def get_post(id: int, db: Session = Depends(get_db)):    # whatever we pass from decorator above is available to the function; id, make sure id passed in from postman is int
                          # i.e. if http://127.0.0.1:8000/posts/bababa is passed, it'll through a meaningfull error
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", str(id))   # since id is int, we need to convert this to string
    # post = cursor.fetchone()
    #================================================
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post {id} was not found!!!")
    return post

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING * """, str(id))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    post_tobe_deleted = db.query(models.Post).filter(models.Post.id == id)
    if post_tobe_deleted.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found!!!")
    post_tobe_deleted.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}", response_model = schemas.Post)
def update_post(id: int, post: schemas.Post, db: Session = Depends(get_db)):
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """, 
    # (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()
    #=======================================
    post_tobe_updated = db.query(models.Post).filter(models.Post.id == id)
    
    if post_tobe_updated.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The post {id} was not found!!!")

    post_tobe_updated.update(post.dict(), synchronize_session=False)
    db.commit()

    return post_tobe_updated.first()

@app.post("/users", response_model=schemas.UserOut)
def create_users(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.get("/users/{id}")
def get_user(id: int, db: Session = Depends(get_db)):
    user  = db.query(models.User).filter(models.User.id == id).first()

    if not user: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} was not found!!!")
    
    return user
