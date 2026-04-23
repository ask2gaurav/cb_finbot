from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from core.security import verify_password, create_access_token
from db.mongo import get_db
from core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
async def login(request: LoginRequest, db = Depends(get_db)):
    user = await db.users.find_one({"email": request.email})
    if not user or not user.get("is_active"):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
        
    if not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
        
    access_token = create_access_token(data={"sub": str(user["_id"]), "role": user["role"]})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(current_user = Depends(get_current_user)):
    # Simple logout for demo: in reality, blacklist the token
    return {"message": "Logged out successfully"}
