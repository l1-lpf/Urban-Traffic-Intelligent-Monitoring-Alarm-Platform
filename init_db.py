from backend.database import engine, Base, SessionLocal
from backend.models.models import User
from backend.core.security import get_password_hash


def init_db():
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    # 检查是否已有 admin
    if not db.query(User).filter(User.username == "admin").first():
        print("正在创建默认管理员账号 (admin / 123456)...")
        admin = User(
            username="admin", hashed_password=get_password_hash("123456"), role="admin"
        )
        db.add(admin)
        db.commit()
    else:
        print("管理员账号已存在。")
    db.close()
    print("✅ 数据库初始化完成！")


if __name__ == "__main__":
    init_db()
