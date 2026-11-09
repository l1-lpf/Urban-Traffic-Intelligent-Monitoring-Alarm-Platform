from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings
from backend.api import auth, cameras, alerts

app = FastAPI(title=settings.PROJECT_NAME)

# 解决跨域问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(cameras.router, prefix="/api/cameras", tags=["摄像头管理"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["报警记录"])


@app.get("/")
def root():
    return {"message": "Urban Traffic AI Platform API is running!"}
