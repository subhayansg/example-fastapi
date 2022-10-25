from fastapi import Depends, HTTPException, status, Response, Depends, APIRouter
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import oauth2
from ..database import get_db
from .. import models, schemas

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)

# go to --> http://127.0.0.1:8000/posts
# @router.get("/", response_model = List[schemas.Post])
@router.get("/", response_model=List[schemas.PostVote])
# @router.get("/")
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, 
              search: Optional[str] = ""):  # limit, skip, search are query parameters
    # post without votes
    # posts = db.query(models.Post). \
    #             filter(models.Post.title.contains(search)). \
    #             filter(models.Post.owner_id == current_user.id). \
    #             limit(limit). \
    #             offset(skip). \
    #             all()
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")). \
                join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True). \
                group_by(models.Post.id). \
                filter(models.Post.title.contains(search)). \
                filter(models.Post.owner_id == current_user.id). \
                limit(limit). \
                offset(skip). \
                all()
    return posts

# go to --> http://127.0.0.1:8000/posts
# from postman add POST, Body - raw, JSON
@router.post("/", status_code=status.HTTP_201_CREATED, response_model= schemas.Post)  # to update the default status_code, to use response class
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    #====================================== OLD PROCESS
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, 
    #                 (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    #======================================
    # new_post = models.Post(title=post.title, content=post.content, published=post.published)
    # instead of the above, typing out all columns, we can use Post.dict() method and unpack that dict
    print(current_user.email)
    new_post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# Get a specific post
# go to --> http://127.0.0.1:8000/posts/2 for example
@router.get("/{id}", response_model=schemas.PostVote )   # id is called "path parameter"
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):    # whatever we pass from decorator above is available to the function; id, make sure id passed in from postman is int
                          # i.e. if http://127.0.0.1:8000/posts/bababa is passed, it'll through a meaningfull error
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", str(id))   # since id is int, we need to convert this to string
    # post = cursor.fetchone()
    #================================================
    # post without votes
    # post = db.query(models.Post).filter(models.Post.owner_id == current_user.id).filter(models.Post.id == id).first()
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")). \
                join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True). \
                group_by(models.Post.id). \
                filter(models.Post.owner_id == current_user.id). \
                filter(models.Post.id == id). \
                first()   
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post {id} was not found!!!")
    return post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING * """, str(id))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    post_tobe_deleted_query = db.query(models.Post).filter(models.Post.id == id)

    post_tobe_deleted = post_tobe_deleted_query.first()

    if post_tobe_deleted == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found!!!")

    if post_tobe_deleted.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action!!!")

    post_tobe_deleted_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model = schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """, 
    # (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()
    #=======================================
    post_tobe_updated_query = db.query(models.Post).filter(models.Post.id == id)

    post_tobe_updated = post_tobe_updated_query.first()
    
    if post_tobe_updated == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The post {id} was not found!!!")

    if post_tobe_updated.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action!!!")

    post_tobe_updated_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()

    return post_tobe_updated