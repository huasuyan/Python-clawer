from sqlalchemy import Column, Integer, BigInteger, String, DateTime, JSON
from sqlalchemy.sql import func
from config.db import Base  # 导入你之前定义的 Base 基类


class CrawlerNone(Base):
    __tablename__ = "crawler_none"

    # 主键 & 基础字段
    crawler_id = Column(Integer, primary_key=True, nullable=False, comment="爬虫ID")
    user_id = Column(BigInteger, nullable=False, comment="用户ID（外键）")

    # 业务字段
    crawler_name = Column(String(50), nullable=False, comment="爬虫名称")
    state = Column(Integer, nullable=False, comment="任务状态：-1失败 0已创建 1采集中 2清洗中 3保存中 4已完成")
    target_source = Column(String(20), nullable=False, comment="数据源：xinhuanet新华网 / integration综合")
    key_word = Column(String(200), nullable=False, comment="关键词")
    params = Column(JSON, default=None, nullable=True, comment="可变JSON参数")

    # 时间字段
    create_time = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        comment="任务创建时间"
    )
    finish_time = Column(DateTime, default=None, nullable=True, comment="任务完成时间")