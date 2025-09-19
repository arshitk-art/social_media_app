from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from uuid import UUID, uuid4


class AbstractModel(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)


class User(AbstractModel, table=True):
    __tablename__ = "userprofile"

    username: str = Field(index=True, unique=True, min_length=3, max_length=50)
    email: str = Field(index=True, unique=True)  # ✅ use str in DB
    full_name: Optional[str] = Field(default=None, max_length=100)
    password : str = Field(max_length=200)
    bio: Optional[str] = Field(default=None, max_length=300)
    followers_count: int = Field(default=0)
    following_count: int = Field(default=0)
    is_banned: bool = Field(default=False)
    is_active: bool = Field(default=True)
    is_delete: bool | None = Field(default = None)
    deleted_at : datetime | None = Field(default=None)

    # relationships
    posts: List["Post"] = Relationship(back_populates="author")
    comments: List["Comment"] = Relationship(back_populates="user")
    liked_posts: List["PostLike"] = Relationship(back_populates="user")
    blocked_users: List["BlockedUser"] = Relationship(back_populates="blocker")
    
    # ✅ must wrap in sa_relationship_kwargs
    blocked_users: List["BlockedUser"] = Relationship(
        back_populates="blocker",
        sa_relationship_kwargs={"foreign_keys": "BlockedUser.blocker_id"},
    )
    blocked_by: List["BlockedUser"] = Relationship(
        back_populates="blocked",
        sa_relationship_kwargs={"foreign_keys": "BlockedUser.blocked_id"},
    )


class BlockedUser(AbstractModel, table=True):
    __tablename__ = "blocked_users"

    blocker_id: UUID = Field(foreign_key="userprofile.id")
    blocked_id: UUID = Field(foreign_key="userprofile.id")

    blocker: Optional[User] = Relationship(back_populates="blocked_by")
    blocked: Optional[User] = Relationship(back_populates="blocked_user")
    
    blocker: Optional[User] = Relationship(
        back_populates="blocked_users",
        sa_relationship_kwargs={"foreign_keys": "BlockedUser.blocker_id"},
    )
    blocked: Optional[User] = Relationship(
        back_populates="blocked_by",
        sa_relationship_kwargs={"foreign_keys": "BlockedUser.blocked_id"},
    )


class Post(AbstractModel, table=True):
    __tablename__ = "posts"

    title: str = Field(min_length=1, max_length=200)
    is_text: bool = Field(default=False)
    text_content: Optional[str] = Field(default=None, max_length=2000)
    media_url: Optional[str] = Field(default=None, max_length=500)
    likes_count: int = Field(default=0)
    comments_count: int = Field(default=0)
    views_count: int = Field(default=0)
    share_count: int = Field(default=0)
    is_reel: bool = Field(default=False)
    caption: Optional[str] = Field(default=None, max_length=1000)

    author_id: UUID = Field(foreign_key="userprofile.id")
    is_delete: bool | None = Field(default = None)
    deleted_at : datetime | None = Field(default=None)

    author: Optional[User] = Relationship(back_populates="posts")
    comments: List["Comment"] = Relationship(back_populates="post")
    likes: List["PostLike"] = Relationship(back_populates="post")


class Comment(AbstractModel, table=True):
    __tablename__ = "comments"

    content: str = Field(min_length=1, max_length=1000)
    likes_count: int = Field(default=0)
    is_reply: bool = Field(default=False)

    post_id: UUID = Field(foreign_key="posts.id")
    author_id: UUID = Field(foreign_key="userprofile.id")
    reply_to_id: Optional[UUID] = Field(default=None, foreign_key="comments.id")

    user: Optional[User] = Relationship(back_populates="comments")
    post: Optional[Post] = Relationship(back_populates="comments")
    is_delete: bool | None = Field(default = None)
    deleted_at : datetime | None = Field(default=None)

    parent_comment: Optional["Comment"] = Relationship(
        back_populates="replies",
        sa_relationship_kwargs={"remote_side": "Comment.id"}
    )
    replies: List["Comment"] = Relationship(back_populates="parent_comment")


class PostLike(AbstractModel, table=True):
    __tablename__ = "post_likes"

    user_id: UUID = Field(foreign_key="userprofile.id")
    post_id: UUID = Field(foreign_key="posts.id")

    user: Optional[User] = Relationship(back_populates="liked_posts")
    post: Optional[Post] = Relationship(back_populates="likes")
