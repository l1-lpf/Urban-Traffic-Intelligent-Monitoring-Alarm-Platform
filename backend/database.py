from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import redis
from backend.core.config import settings

# MySQL 连接
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Redis 连接
redis_client = redis.Redis(host="127.0.0.1", port=6379, db=0, decode_responses=True)
# 专门用于视频流图片的二进制客户端（必须设为 False）
redis_binary_client = redis.Redis(
    host="127.0.0.1", port=6379, db=0, decode_responses=False
)
