# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from app.api.routes import auth, users, posts, comments, likes, messages
from config import settings
from contextlib import asynccontextmanager
from dotenv import load_dotenv
# from config import initdb
from app.auth.routes import router as auth_router
from app.users.routes import router as users_router



@asynccontextmanager
async def lifespan(app: FastAPI):    
    print("Server is starting...")
    load_dotenv()
    print("loaded all the env variables")
    # await initdb()
    print("Database connected")
    yield
    print("server is stopping")
    
app = FastAPI(
    title="Social Media API",
    version="1.0.0",
    description="Backend for a social media app built with FastAPI",
    lifespan=lifespan
)
    
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# # Include all API routers
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(users_router, prefix="/users", tags=["Users"])
# app.include_router(posts.router, prefix="/posts", tags=["Posts"])
# app.include_router(comments.router, prefix="/comments", tags=["Comments"])
# app.include_router(likes.router, prefix="/likes", tags=["Likes"])
# app.include_router(messages.router, prefix="/messages", tags=["Messages"])

# Health check route
@app.get("/", tags=["Health"])
def read_root():
    return {"message": "Social Media API is running."}
