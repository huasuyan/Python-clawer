from pydantic import BaseModel, Field
from typing import Optional


class TianApiRequest(BaseModel):
    """天行数据API请求参数"""
    
    key: str = Field(..., description="API密钥")
    
    num: int = Field(50, ge=1, le=50, description="返回数量，固定为50")
    
    form: Optional[int] = Field(1, description="兼容历史问题，建议传1")
    
    page: Optional[int] = Field(0, ge=0, description="翻页")
    
    rand: Optional[int] = Field(0, description="随机获取，0=不随机，1=随机")
    
    word: Optional[str] = Field(None, description="搜索关键词")
    
    source: Optional[str] = Field(None, description="指定来源（仅综合新闻接口）")


class NewsItem(BaseModel):
    """新闻条目"""
    
    title: str = Field(..., description="标题")
    content: str = Field("", description="内容")
    publishTime: str = Field("", description="发布时间")
    source: str = Field("", description="来源")
    url: str = Field("", description="链接")
    picUrl: str = Field("", description="图片链接")


class TianApiResponse(BaseModel):
    """天行数据API响应"""
    
    code: int = Field(..., description="状态码")
    msg: str = Field(..., description="消息")
    dataList: list = Field([], description="数据列表")
