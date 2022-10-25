from fastapi import Depends, FastAPI, Depends

from app.routers.vote import vote
# ORM/sqlalchemy related
from . import models
from .database import engine, get_db
from sqlalchemy.orm import Session
from .routers import post, user, auth, vote
from .config import settings

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# as we started using alembic, we no longer need the below command
# models.Base.metadata.create_all(bind=engine)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/")
def default_get():
    return {"message": "Hello World"}

@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data": posts}



