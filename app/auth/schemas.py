from pydantic import BaseModel, EmailStr, Field
from uuid import UUID,uuid4
from datetime import datetime

class LoginSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email : EmailStr | None = None
    password: str = Field(..., min_length=6)
    confirm_password: str | None = Field(min_length=6,default=None)
    
class ResponseSchemaAuth(BaseModel):
    access_token : str
    refresh_token : str
    
class ResetPassword(BaseModel):
    email : EmailStr
    new_password : str = Field(..., min_length=6)
    confirm_password : str = Field(..., min_length=6)
    
class ResponseSchema(BaseModel):
    message : str 
    status : str 
    status_code : int
    data_dict : dict | None = None
    data_list : list | None = None
    


    

    