from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .settings import settings


# 数据库连接地址
SQLALCHEMY_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URL

# 创建引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_recycle=3600,  # 自动重连
    pool_pre_ping=True
)

# 会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 模型基类
Base = declarative_base()

# 获取数据库连接
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        print(e)
        raise
    finally:
        db.close()