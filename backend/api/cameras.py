from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database import get_db
from backend.models.models import Camera, User
from backend.core.security import get_current_user

router = APIRouter()


# 定义前端传来的数据格式
class CameraCreate(BaseModel):
    name: str
    rtsp_url: str
    location: str = "Unknown"


# 1. 获取所有摄像头（必须带 Token 才能访问）
@router.get("/")
def get_cameras(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),  # 核心：这个依赖会拦截没带 Token 的请求
):
    cameras = db.query(Camera).all()
    return {"total": len(cameras), "data": cameras}


# 2. 添加新摄像头
@router.post("/")
def create_camera(
    camera: CameraCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 只有 admin 才能添加设备
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足，只有管理员可以添加设备")

    new_camera = Camera(
        name=camera.name, rtsp_url=camera.rtsp_url, location=camera.location
    )
    db.add(new_camera)
    db.commit()
    db.refresh(new_camera)
    return {"message": "摄像头添加成功", "camera_id": new_camera.id}
