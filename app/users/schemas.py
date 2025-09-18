from pydantic import BaseModel, EmailStr, Field, model_validator
from uuid import UUID,uuid4
from datetime import datetime

class ResponseSchema(BaseModel):
    message : str 
    status : str 
    status_code : int
    data_dict : dict | None = None
    data_list : list | None = None
    pagination_data : dict | None = None
    
class CreateUserSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email : EmailStr
    full_name : str | None = None
    bio : str | None = None
    password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)
    
class UserSchema(BaseModel):
    id: UUID
    username: str
    email : EmailStr
    full_name : str | None = None
    bio : str | None = None
    followers_count: int
    following_count: int
    is_banned: bool
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        orm_mode = True

class PostCreateSchema(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    is_text : bool
    text_content : str | None = None
    media_url : str | None = None
    is_reel : bool
    caption : str | None = None
    author_id: UUID
    
    @model_validator(mode="after")
    def validate_post(self):
        if self.is_text and self.is_reel:
            raise Exception("InvalidPostData : post can't be text and reel at the same time")
        if self.is_text and self.media_url!=None:
            raise Exception("InvalidPostData : you selected post to be text you can't upload media with it ")
        return self

class PostFetchSchema(BaseModel):
    id : UUID
    title: str = Field(min_length=1, max_length=200)
    is_text : bool
    text_content : str | None = None
    media_url : str | None = None
    is_reel : bool
    caption : str | None = None
    author_id: UUID
    author_username: str
    likes_count: int
    comment_count: int
    views_count : int
    share_count: int
    created_at : datetime
    updated_at : datetime
    
class CommentCreateSchema(BaseModel):
    content: str = Field(min_length=1, max_length=1000)
    is_reply: bool
    post_id: UUID
    author_id: UUID
    reply_to_id: UUID | None = None
    
    @model_validator(mode="after")
    def validate_comment(self):
        if self.is_reply and not self.reply_to_id:
            raise Exception("InvalidComment - you need to provide comment id if this comment is a reply")
        return self

class CommentFetchSchema(BaseModel):
    id : UUID
    content: str = Field(min_length=1, max_length=1000)
    is_reply: bool
    post_id: UUID
    author_id: UUID
    reply_to_id: UUID | None
    created_at : datetime
    updated_at : datetime

class PostLikeSchema(BaseModel):
    user_id : UUID
    post_id : UUID
    
class PostLikeFetchSchema(BaseModel):
    id : UUID
    user_id : UUID
    post_id : UUID
    
    

