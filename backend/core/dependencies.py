from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from core.security import decode_access_token
from db.mongo import get_db
from models.user import UserResponse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
        
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
        
    is_blacklisted = await db.token_blacklist.find_one({"token": token})
    if is_blacklisted:
        raise credentials_exception
        
    user_doc = await db.users.find_one({"_id": user_id})
    if user_doc is None:
        raise credentials_exception
        
    return UserResponse(
        id=str(user_doc["_id"]),
        email=user_doc["email"],
        role=user_doc["role"],
        is_active=user_doc["is_active"]
    )

def require_role(*roles: str):
    def dependency(token_data = Depends(get_current_user)):
        if token_data.role not in roles:
            raise HTTPException(403, "Insufficient permissions")
        return token_data
    return dependency
