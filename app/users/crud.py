from sqlmodel import Session, select, func
from typing import Optional
from .models import User, Post, Comment, PostLike
from app.users.schemas import CreateUserSchema, UserSchema, PostCreateSchema, CommentCreateSchema, PostLikeSchema
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy import and_

class UserServiceHandler:
    def __init__(self, session: Session):
        self.session = session
        self.blacklist_token = set()  # In-memory blacklist for simplicity

    def get_user_by_id(self, user_id: str) -> UserSchema | None:
        statement = select(User).where(User.id == user_id)
        result = self.session.exec(statement).first()
        return UserSchema.model_validate(result) if result else None

    def create_user(self, user_data: CreateUserSchema) -> UserSchema:
        new_user = User(**user_data.model_dump())
        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)
        return UserSchema.model_validate(new_user)

    def update_user(self, user_id: str, update_data: dict) -> UserSchema | None:
        user = self.session.get(User, user_id)
        if user:
            for key, value in update_data.items():
                setattr(user, key, value)
            self.session.commit()
            self.session.refresh(user)
            return UserSchema.model_validate(user)
        return None

    def delete_user(self, user_id: str) -> bool:
        user = self.session.get(User, user_id)
        if user:
            self.session.delete(user)
            self.session.commit()
            return True
        return False

    def get_user_by_email(self, email: str) -> UserSchema | None:
        statement = select(User).where(User.email == email)
        result = self.session.exec(statement).first()
        return UserSchema.model_validate(result) if result else None
    
class PostServiceHandler:
    def __init__(self, session : Session):
        self.session = session
    
    def filter_by(self,filters:dict, ofset : int | None=None, limit : int | None = None) -> Post:
        conditions: list[BinaryExpression] = []

        for field_name, value in filters.items():
            if hasattr(Post, field_name):
                field = getattr(Post, field_name)
                conditions.append(field == value)   # equality check
            # you can extend this with operators (>, <, etc.)
    
        statement = select(Post)
        if conditions:
            statement = statement.where(and_(*conditions))
        
        if ofset and limit:
            statement =  statement.order_by(Post.created_at.desc()).offset(ofset).limit(limit)
    
        return self.session.exec(statement).all()
    
    def create(self,post_data: PostCreateSchema)->Post:
        post = Post(**post_data.model_dump())
        self.session.add(post)
        self.session.commit()
        self.session.refresh(post)
        return post
    
    def get_all(self)-> Post:
        return self.session.exec(select(Post)).all()
    
    def count(self) -> int:
        return self.session.exec(select(func.count()).select_from(Post)).one()
    
    def update(self, post_id: str, update_data: dict):
        post = self.session.get(Post, post_id)
        if post:
            for key, value in update_data.items():
                setattr(post, key, value)
            self.session.commit()
            self.session.refresh(post)
            return post
        return None

class CommentServiceHandler:
    def __init__(self, session:Session):
        self.session = session
    
    def filter_by(self,filters:dict, ofset : int | None=None, limit : int | None = None)-> Comment:
        conditions: list[BinaryExpression] = []
        for field_name, value in filters.items():
            if hasattr(Comment, field_name):
                field = getattr(Comment, field_name)
                conditions.append(field==value)
        statement = select(Comment)
        
        if conditions:
            statement = statement.where(and_(*conditions))
        
        if ofset and limit:
            statement =  statement.order_by(Post.created_at.desc()).offset(ofset).limit(limit)
            
        return self.session.exec(statement).all()
    
    def get_all(self)-> Comment:
        return self.session.exec(select(Comment)).all()
    
    def create(self, comment_data: CommentCreateSchema) -> Comment:
        comment = Comment(**comment_data.model_dump())
        self.session.add(comment)
        self.session.commit()
        self.session.refresh(comment)
        return comment
    
    def count(self) -> int:
        return self.session.exec(select(func.count()).select_from(Comment)).one()
    
    def update(self, post_id: str, update_data: dict):
        comment = self.session.get(Comment, post_id)
        if comment:
            for key, value in update_data.items():
                setattr(comment, key, value)
            self.session.commit()
            self.session.refresh(comment)
            return comment
        return None


class PostLikeHandler:
    def __init__(self, session : Session):
        self.session = session
        
    def filter_by(self,filter:dict, ofset : int | None=None, limit : int | None = None) -> PostLike:
        conditions = [BinaryExpression] = []
        for field_name, value in filter.items():
            if hasattr(PostLike, field_name):
                field = getattr(PostLike,field_name)
                conditions.append(field==value)
            statement = select(PostLike)
        
        if conditions:
            statement = statement.where(and_(*conditions))
        
        if ofset and limit:
            statement =  statement.order_by(Post.created_at.desc()).offset(ofset).limit(limit)
            
        return self.session.exec(statement).all()
    
    def get_all(self) -> PostLike:
        return self.session.exec(select(Comment)).all()
    
    def create(self, postlike_data: PostLikeSchema) -> PostLike:
        pl = PostLike(**postlike_data.model_dump())
        self.session.add(pl)
        self.session.commit()
        self.session.refresh(pl)
        return pl
    
    def count(self) -> int:
        return self.session.exec(select(func.count()).select_from(Post)).one()

                
