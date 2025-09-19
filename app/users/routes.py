from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select
from typing import List
# from app.database import get_session  # Your session dependency
from app.users.models import User  # Your SQLModel user model
# from app.users.schemas import UserCreate, UserRead  # Pydantic schemas
from uuid import UUID
from deps import get_session
from .crud import UserServiceHandler, PostServiceHandler, CommentServiceHandler, PostLikeHandler
from app.users.schemas import *
from fastapi_utils.cbv import cbv
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth.auth_bearer import JWTBearer
from pydantic import ValidationError

router = APIRouter()

security = HTTPBearer()
jwt_handler = JWTBearer()

'''
create apis for -->
- Get user by username or id
- Create a new user
- Update user by ID
- Delete user by ID
- create a post
- comment on post
- like a post
- like a comment
- block a user
- upload media (image/video)
'''

class UserAPIWrapper:
    @router.get("/fetch_user/", response_model=UserSchema)
    async def fetch_user(credentials: HTTPAuthorizationCredentials = Depends(security), session: Session = Depends(get_session)):
        handler = UserServiceHandler(session)
        if not credentials.credentials:
            return ResponseSchema(
                message="Access Denied",
                status="Error",
                status_code=403
            )
        user_data = jwt_handler.verify_jwt(credentials.credentials,session)
        print(f"\n\nuser_data:\n{user_data}\n\n")
        user = await handler.get_user_by_id(user_id=user_data.get("user_id"))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
    @router.patch("/update_user/", response_model=UserSchema)
    async def update_user( update_data: dict,credentials: HTTPAuthorizationCredentials = Depends(security), session: Session = Depends(get_session)):
        handler = UserServiceHandler(session)
        if not credentials.credentials:
            return ResponseSchema(
                message="Access Denied",
                status="Error",
                status_code=403
            )
        user = jwt_handler.verify_jwt(credentials.credentials,session)
        updated_user = await handler.update_user(user_id=user.get("user_id"), update_data=update_data)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user
    
    # for searching user use

@cbv(router)
class PostAPIWrapper:
    session: Session = Depends(get_session)
        
    def __init__(self):
        self.post_handler = None
        self.comment_handler = None
        self.like_handler = None

    # 👇 run after dependencies injected
    def __post_init__(self):
        self.post_handler = PostServiceHandler(self.session)
        self.comment_handler = CommentServiceHandler(self.session)
        self.like_handler = PostLikeHandler(self.session)

    
    @router.post('/create_post/', response_model=ResponseSchema)
    async def create_post(self,post_data : dict, credentials: HTTPAuthorizationCredentials = Depends(security)):
        try:
            # fetch user
            if not credentials.credentials:
                return ResponseSchema(
                    message="Access Denied",
                    status="Error",
                    status_code=403
                )
            user = jwt_handler.verify_jwt(credentials.credentials)
            if not user:
                return ResponseSchema(
                    message="Access Denied",
                    status="Error",
                    status_code=403
                )
            post_data.update({
                "author_id":user.get("user_id")
            })
                
            #validate input payload
            post_data = PostCreateSchema(**post_data)
            post = self.post_handler.create(post_data=post_data)
            post_data = PostFetchSchema.model_validate(post)
            
            return ResponseSchema(
                message="post created successfully",
                status="success",
                status_code=200,
                data_dict=post_data.model_dump()
            )
        except ValidationError:
            return ResponseSchema(
                message=f"Invalid Request Payload",
                status="Error",
                status_code=400
            )
        except Exception as e:
            return ResponseSchema(
                message=f"Error - {e}",
                status="Error",
                status_code=500
            )
    
    @router.get('/fetch_all_post_for_user/', response_model=ResponseSchema)
    async def get_all_post_for_user(self,req_type : str, page : int | None =None, page_size : int | None = None, post_id : UUID | None = None, credentials: HTTPAuthorizationCredentials = Depends(security)):
        '''
        request type:
        all_post -> want to fetch all post
        specific_post -> want to fetch specific post
        '''
        try:
            # fetch user
            user = jwt_handler.verify_jwt(credentials.credentials)
            
            if not user:
                return ResponseSchema(
                    message="Access Denied",
                    status="Error",
                    status_code=403
                )
            if req_type =="all_post":
                if not page or not page_size:
                    return ResponseSchema(
                        message="Page number and page size is required",
                        status="Error",
                        status_code=400,
                    )
                ofset = page*page_size
                limit = ofset+page_size
                posts = self.post_handler.filter_by(
                    {
                        "author_id": user.get("user_id")
                    },
                    ofset=ofset,
                    limit=limit
                )
                resp = [PostFetchSchema.model_validate(post) for post in posts]
                return ResponseSchema(
                    message="post fetched succesfully",
                    status="success",
                    status_code=200,
                    data_list=resp,
                    pagination_data={
                        "page":page,
                        "next_page":page+1,
                        "page_size":page_size,
                    }
                )
            else:
                if not post_id:
                    return ResponseSchema(
                        message = "post id is req to fetch specific post",
                        status = "Error",
                        status_code = 400
                    )
                post= self.post_handler.filter_by(
                    {
                        "id": post_id,
                        "author_id":user.get("user_id")
                    }
                )
                post_data = PostFetchSchema.model_validate(post[0])
                return ResponseSchema(
                    message="post fetched successfully",
                    status="success",
                    status_code=200,
                    data_dict=post_data.model_dump()
                )
                
        except ValidationError:
            return ResponseSchema(
                message=f"Invalid Request Payload",
                status="Error",
                status_code=400
            )
            
        except Exception as e:
            return ResponseSchema(
                message=f"Error - {e}",
                status="Error",
                status_code=500
            )
    
    @router.delete('\delete_post\{post_id}')
    async def delete_post(self,post_id:str, credentials: HTTPAuthorizationCredentials = Depends(security)):
        try:
            # fetch user
            user = jwt_handler.verify_jwt(credentials.credentials)

            if not user:
                return ResponseSchema(
                    message="Access Denied",
                    status="Error",
                    status_code=403
                )

            post = self.post_handler.update(
                post_id=post_id,
                update_data={
                    "is_delete":True,
                    "deleted_at":datetime.now()
                }
            )
            if not post:
                return ResponseSchema(
                    message="wrong post id",
                    status="Error",
                    status_code=400
                )

            return ResponseSchema(
                message="Post deleted successfully",
                status="success",
                status_code=200
            )
        
        except ValidationError:
            return ResponseSchema(
                message=f"Invalid Request Payload",
                status="Error",
                status_code=400
            )
           
        except Exception as e:
            return ResponseSchema(
                message=f"Error - {e}",
                status="Error",
                status_code=500
            )
            
        
        
    

    