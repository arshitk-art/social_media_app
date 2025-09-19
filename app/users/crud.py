from sqlmodel import select, func
from typing import Optional
from .models import User, Post, Comment, PostLike
from app.users.schemas import (
    CreateUserSchema, UserSchema, PostCreateSchema,
    CommentCreateSchema, PostLikeSchema
)
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession


class UserServiceHandler:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.blacklist_token = set()  # In-memory blacklist for simplicity

    async def get_user_by_id(self, user_id: str) -> Optional[UserSchema]:
        statement = select(User).where(User.id == user_id)
        result = await self.session.execute(statement)
        user = result.scalars().first()
        return UserSchema.model_validate(user) if user else None
    
    async def get_user_by_username(self, user_name: str) -> Optional[UserSchema]:
        statement = select(User).where(User.username == user_name)
        result = await self.session.execute(statement)
        user = result.scalars().first()
        return UserSchema.model_validate(user) if user else None

    async def create_user(self, user_data: CreateUserSchema) -> UserSchema:
        new_user = User(**user_data.model_dump())
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return UserSchema.model_validate(new_user)

    async def update_user(self, user_id: str, update_data: dict) -> Optional[UserSchema]:
        user = await self.session.get(User, user_id)
        if user:
            for key, value in update_data.items():
                setattr(user, key, value)
            await self.session.commit()
            await self.session.refresh(user)
            return UserSchema.model_validate(user)
        return None

    async def delete_user(self, user_id: str) -> bool:
        user = await self.session.get(User, user_id)
        if user:
            await self.session.delete(user)
            await self.session.commit()
            return True
        return False

    async def get_user_by_email(self, email: str) -> Optional[UserSchema]:
        statement = select(User).where(User.email == email)
        result = await self.session.execute(statement)
        user = result.scalars().first()
        return UserSchema.model_validate(user) if user else None


class PostServiceHandler:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def filter_by(self, filters: dict, offset: int | None = None, limit: int | None = None) -> list[Post]:
        conditions: list[BinaryExpression] = []
        for field_name, value in filters.items():
            if hasattr(Post, field_name):
                field = getattr(Post, field_name)
                conditions.append(field == value)

        statement = select(Post)
        if conditions:
            statement = statement.where(and_(*conditions))

        if offset and limit:
            statement = statement.order_by(Post.created_at.desc()).offset(offset).limit(limit)

        result = await self.session.execute(statement)
        return result.scalars().all()

    async def create(self, post_data: PostCreateSchema) -> Post:
        post = Post(**post_data.model_dump())
        self.session.add(post)
        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def get_all(self) -> list[Post]:
        result = await self.session.execute(select(Post))
        return result.scalars().all()

    async def count(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(Post))
        return result.scalar_one()

    async def update(self, post_id: str, update_data: dict) -> Optional[Post]:
        post = await self.session.get(Post, post_id)
        if post:
            for key, value in update_data.items():
                setattr(post, key, value)
            await self.session.commit()
            await self.session.refresh(post)
            return post
        return None


class CommentServiceHandler:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def filter_by(self, filters: dict, offset: int | None = None, limit: int | None = None) -> list[Comment]:
        conditions: list[BinaryExpression] = []
        for field_name, value in filters.items():
            if hasattr(Comment, field_name):
                field = getattr(Comment, field_name)
                conditions.append(field == value)

        statement = select(Comment)
        if conditions:
            statement = statement.where(and_(*conditions))

        if offset and limit:
            statement = statement.order_by(Comment.created_at.desc()).offset(offset).limit(limit)

        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_all(self) -> list[Comment]:
        result = await self.session.execute(select(Comment))
        return result.scalars().all()

    async def create(self, comment_data: CommentCreateSchema) -> Comment:
        comment = Comment(**comment_data.model_dump())
        self.session.add(comment)
        await self.session.commit()
        await self.session.refresh(comment)
        return comment

    async def count(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(Comment))
        return result.scalar_one()

    async def update(self, comment_id: str, update_data: dict) -> Optional[Comment]:
        comment = await self.session.get(Comment, comment_id)
        if comment:
            for key, value in update_data.items():
                setattr(comment, key, value)
            await self.session.commit()
            await self.session.refresh(comment)
            return comment
        return None


class PostLikeHandler:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def filter_by(self, filters: dict, offset: int | None = None, limit: int | None = None) -> list[PostLike]:
        conditions: list[BinaryExpression] = []
        for field_name, value in filters.items():
            if hasattr(PostLike, field_name):
                field = getattr(PostLike, field_name)
                conditions.append(field == value)

        statement = select(PostLike)
        if conditions:
            statement = statement.where(and_(*conditions))

        if offset and limit:
            statement = statement.order_by(PostLike.created_at.desc()).offset(offset).limit(limit)

        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_all(self) -> list[PostLike]:
        result = await self.session.execute(select(PostLike))
        return result.scalars().all()

    async def create(self, postlike_data: PostLikeSchema) -> PostLike:
        pl = PostLike(**postlike_data.model_dump())
        self.session.add(pl)
        await self.session.commit()
        await self.session.refresh(pl)
        return pl

    async def count(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(PostLike))
        return result.scalar_one()
