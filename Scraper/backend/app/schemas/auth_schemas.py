"""
Authentication schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional


class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "officer@hpcl.com",
                "password": "officer123"
            }
        }


class Token(BaseModel):
    """Token response schema"""
    token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """User profile response"""
    id: int
    name: str
    email: str
    role: str
    territory: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Regional Officer",
                "email": "officer@hpcl.com",
                "role": "SALES_OFFICER",
                "territory": "Mumbai West"
            }
        }


class LoginResponse(BaseModel):
    """Complete login response"""
    token: str
    user: UserResponse
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "user": {
                    "id": 1,
                    "name": "Regional Officer",
                    "email": "officer@hpcl.com",
                    "role": "SALES_OFFICER",
                    "territory": "Mumbai West"
                }
            }
        }
