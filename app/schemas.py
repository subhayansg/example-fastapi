from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, conint

from app.database import Base

class PostBase(BaseModel):
    title: str                      
    content: str                    
    published: bool = True
        
class PostCreate(PostBase):
    pass

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at = datetime
    class Config():
        orm_mode = True

# below class is for response that we are sending back to front end
# to control what fields we send back
# so, we don't get back id and created_at columns in response as those tow are not mentioned in below class
class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut
    class Config():
        orm_mode = True

class PostVote(BaseModel):
    Post: Post
    votes: int
    class Config():
        orm_mode = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None

class Vote(BaseModel):
    post_id: int
    direction: conint(le=1)
