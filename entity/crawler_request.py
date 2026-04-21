from pydantic import BaseModel, Field
from typing import List, Optional


class CrawlerIntegrationRequest(BaseModel):
    """爬虫整合请求参数"""

    # user_id: int = Field(..., description="用户ID")

    crawler_id: int = Field(..., description="爬虫ID")

    # key_word: str = Field(..., description="检索关键词")
    #
    # sources: List[str] = Field(..., description="数据源列表，可选值：['综合', '社会']")
    #
    # page: int = Field(1, ge=1, description="获取多少页的内容")


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
