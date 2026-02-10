"""
Authentication router
"""
from fastapi import APIRouter, HTTPException, status, Depends
from ..schemas.auth_schemas import LoginRequest, LoginResponse, UserResponse
from ..models.database import db
from ..utils.security import verify_password, create_access_token
from ..middleware.auth import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """
    User login endpoint
    
    Returns JWT token and user profile
    """
    # Get user by email
    user = db.get_user_by_email(credentials.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user.get('active', True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Update last login
    db.update_user_last_login(user['id'])
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user['id'])})
    
    # Prepare user response
    user_response = UserResponse(
        id=user['id'],
        name=user['name'],
        email=user['email'],
        role=user['role'],
        territory=user.get('territory')
    )
    
    return LoginResponse(
        token=access_token,
        user=user_response
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current user profile
    
    Requires authentication
    """
    return UserResponse(
        id=current_user['id'],
        name=current_user['name'],
        email=current_user['email'],
        role=current_user['role'],
        territory=current_user.get('territory')
    )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    User logout
    
    In JWT stateless auth, this is primarily client-side token deletion
    """
    return {
        "success": True,
        "message": "Logged out successfully"
    }
