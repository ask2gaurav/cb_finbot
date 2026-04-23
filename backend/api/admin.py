from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models.user import UserResponse, UserCreate, UserModel
from core.security import get_password_hash
from core.dependencies import require_role
from db.mongo import get_db
from services.ingestion.indexer import qdrant_client
from core.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users", response_model=List[UserResponse])
async def list_users(current_user: UserResponse = Depends(require_role("admin")), db = Depends(get_db)):
    users_cursor = db.users.find({})
    users = await users_cursor.to_list(length=100)
    result = []
    for u in users:
        result.append(UserResponse(id=str(u["_id"]), email=u["email"], role=u["role"], is_active=u["is_active"]))
    return result

@router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, current_user: UserResponse = Depends(require_role("admin")), db = Depends(get_db)):
    existing = await db.users.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_pwd = get_password_hash(user.password)
    new_user = UserModel(email=user.email, hashed_password=hashed_pwd, role=user.role)
    await db.users.insert_one(new_user.model_dump(by_alias=True))
    
    return UserResponse(id=str(new_user.id), email=new_user.email, role=new_user.role, is_active=new_user.is_active)

@router.patch("/users/{user_id}")
async def update_user(user_id: str, active: bool, current_user: UserResponse = Depends(require_role("admin")), db = Depends(get_db)):
    await db.users.update_one({"_id": user_id}, {"$set": {"is_active": active}})
    return {"message": "User updated"}

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, current_user: UserResponse = Depends(require_role("admin")), db = Depends(get_db)):
    await db.users.update_one({"_id": user_id}, {"$set": {"is_active": False}})
    return {"message": "User deactivated"}

@router.get("/collections")
async def get_collections_stats(current_user: UserResponse = Depends(require_role("admin"))):
    stats = []
    roles = ["finance", "engineering", "marketing", "employee", "c_level"]
    for role in roles:
        coll_name = f"rag_{role}"
        try:
            info = await qdrant_client.get_collection(collection_name=coll_name)
            stats.append({"role": role, "collection": coll_name, "points_count": info.points_count})
        except Exception:
            stats.append({"role": role, "collection": coll_name, "points_count": 0, "status": "not_created"})
            
    return stats
