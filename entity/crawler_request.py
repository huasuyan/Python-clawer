from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CrawlerIntegrationRequest(BaseModel):
    """爬虫整合请求参数"""

    task_id: int = Field(..., description="任务ID")

    task_way: str = Field(..., description="任务类型: report/alert")

    filter_time: Optional[str] = Field(None, description="过滤时间，格式：YYYY-MM-DD HH:MM:SS，只保留晚于此时间的新闻")


class NewsItem(BaseModel):
    """新闻条目"""
    
    title: str = Field("", description="标题")
    content: str = Field("", description="内容")
    publishTime: str = Field("", description="发布时间")
    source: str = Field("", description="来源")
    url: str = Field("", description="链接")
    picUrl: str = Field("", description="图片链接")


class CrawlerIntegrationResponse(BaseModel):
    """爬虫整合响应"""
    
    code: int = Field(1, description="状态码")
    msg: str = Field("success", description="消息")
    data: dict = Field(..., description="数据")
