from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.models import AlertRecord, User
from backend.core.security import get_current_user

router = APIRouter()


# 获取历史报警记录（支持分页）
@router.get("/")
def get_alerts(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 按时间倒序，最新的报警排在前面
    alerts = (
        db.query(AlertRecord)
        .order_by(AlertRecord.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    total = db.query(AlertRecord).count()
    return {"total": total, "data": alerts}
