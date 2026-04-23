import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from core.config import get_settings
from api import auth, chat, documents, admin
from db.mongo import get_db, client
from models.user import UserModel
from core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("Starting up application...")
    
    # Initialize DB users
    db = get_db()
    admin_exists = await db.users.find_one({"email": "admin@demo.com"})
    if not admin_exists:
        admin_user = UserModel(email="admin@demo.com", hashed_password=get_password_hash("admin123"), role="admin")
        await db.users.insert_one(admin_user.model_dump(by_alias=True))
        demo_roles = ["finance", "engineering", "marketing", "employee", "c_level"]
        for r in demo_roles:
            user = UserModel(email=f"{r}@demo.com", hashed_password=get_password_hash("demo123"), role=r)
            await db.users.insert_one(user.model_dump(by_alias=True))
    
    yield
    # Shutdown actions
    client.close()
    logger.info("Shutting down application...")

app = FastAPI(
    title="Role-Gated RAG Platform",
    lifespan=lifespan,
    version="1.0.0"
)

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "dependencies": {
            "mongodb": "pending",
            "qdrant": "pending",
            "semantic_router": "pending"
        }
    }

app.include_router(auth.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
