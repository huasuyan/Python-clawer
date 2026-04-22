from sqlalchemy import Column, Integer, BigInteger, String, DateTime, JSON, Text
from sqlalchemy.sql import func
from config.db import Base  # 导入你之前定义的 Base 基类


class SpecialReportSetting(Base):
    __tablename__ = "special_report_setting"

    special_report_id = Column(BigInteger, primary_key=True, nullable=False, comment="专题报告ID")
    monitor_keywords = Column(JSON, nullable=False, comment="监控关键词")
    params = Column(JSON, nullable=False, comment="参数配置")
    data_source = Column(String(500), nullable=False, comment="数据源")


class SpecialAlertSetting(Base):
    __tablename__ = "special_alert_setting"

    alert_id = Column(Integer, primary_key=True, nullable=False, comment="预警ID")
    key_word = Column(JSON, nullable=False, comment="关键词")
    params = Column(JSON, nullable=False, comment="参数配置")
    target_source = Column(String(20), nullable=False, comment="目标数据源")


class NewsData(Base):
    __tablename__ = "news_data"

    news_id = Column(BigInteger, primary_key=True, autoincrement=True, comment="新闻ID")
    special_report_id = Column(BigInteger, nullable=True, comment="专题报告ID")
    alert_id = Column(BigInteger, nullable=True, comment="预警ID")
    title = Column(String(500), nullable=True, comment="标题")
    content = Column(Text, nullable=True, comment="内容")
    video = Column(String(1000), nullable=True, comment="视频")
    platform = Column(String(100), nullable=True, comment="平台")
    source = Column(String(100), nullable=True, comment="来源")
    publisher = Column(String(100), nullable=True, comment="发布者")
    publish_time = Column(DateTime, nullable=True, comment="发布时间")
    comment = Column(Integer, nullable=True, comment="评论数")
    region = Column(String(100), nullable=True, comment="地区")
    original_url = Column(String(1000), nullable=True, comment="原始URL")
    article_type = Column(String(100), nullable=True, comment="文章类型")
    source_url = Column(String(500), nullable=True, comment="来源URL")
    create_time = Column(DateTime, nullable=False, server_default=func.current_timestamp(), comment="创建时间")


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


class CrawlerCron(Base):
    __tablename__ = "crawler_cron"

    # 主键&基础字段
    crawler_id = Column(
        Integer,
        primary_key=True,
        nullable=False,
        autoincrement=True,
        comment="爬虫ID"
    )
    user_id = Column(
        BigInteger,
        nullable=False,
        comment="用户ID"
    )

    # 核心业务字段
    crawler_name = Column(
        String(50),
        nullable=False,
        comment="爬虫名称"
    )
    trigger_state = Column(
        Integer,
        nullable=False,
        comment="调度状态: 0已停止 1已启用"
    )
    target_source = Column(
        String(20),
        nullable=False,
        comment="数据源: xinhuanet=新华网"
    )
    key_word = Column(
        JSON,
        nullable=False,
        comment="预警词组"
    )
    params = Column(
        JSON,
        nullable=True,
        default=None,
        comment="可变参数"
    )

    # 预警&调度配置字段
    frequency = Column(
        Integer,
        nullable=False,
        comment="预警频率: 0实时 1定时 2定量"
    )
    alert_trigger = Column(
        Integer,
        nullable=True,
        default=None,
        comment="触发阈值frequency=2时表示定量阈值frequency=1定时"
    )
    time_range = Column(
        JSON,
        nullable=True,
        default=None,
        comment="预警时间范围, 如{\"weekdays\":[0,1,1,1,1,1,0]}, 实时"
    )
    alert_method = Column(
        Integer,
        nullable=False,
        comment="预警方式: 0全部 1站内信 2邮箱"
    )
    dedup_enable = Column(
        Integer,
        nullable=False,
        comment="去重开关: 0不去重 1去重"
    )

    # 运行状态&时间字段
    state = Column(
        Integer,
        nullable=False,
        comment="运行状态: -1监测失败等待下次 0等待下次执行 1爬取中"
    )
    latest_news_time = Column(
        DateTime,
        nullable=True,
        default=None,
        comment="数据库中publishTime最接近现在的时间"
    )
    create_time = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        comment="任务创建时间"
    )

