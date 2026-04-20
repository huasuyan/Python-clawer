from pydantic import BaseModel, Field
from typing import Optional


class XinhuaSearchRequest(BaseModel):
    """新华网搜索请求参数"""

    keyword: str = Field(..., description="搜索关键词")

    search_type: int = Field(1, description="检索类型：1=新闻，2=学术文献")

    search_fields: Optional[int] = Field(None, description="搜索字段（仅search_type=1时有效）：0=正文，1=标题")

    sort_field: Optional[int] = Field(None, description="排序方式（仅search_type=1时有效）：0=时间，1=相关度")

    start_page: int = Field(0, ge=0, description="起始页码（从0开始，0表示第1页）")

    end_page: int = Field(0, ge=0, description="结束页码（包含，0表示第1页）")

    browser_type: str = Field("edge", description="浏览器类型：chrome 或 edge")
    
    def get_search_fields_value(self) -> str:
        """获取searchFields参数值"""
        if self.search_type == 1 and self.search_fields is not None:
            return str(self.search_fields)
        return ""
    
    def get_sort_field_value(self) -> str:
        """获取sortField参数值"""
        if self.search_type == 1 and self.sort_field is not None:
            return str(self.sort_field)
        return ""
    
    def validate_params(self):
        """验证参数"""
        if self.end_page < self.start_page:
            raise ValueError("结束页码不能小于起始页码")
        
        if self.search_type not in [1, 2]:
            raise ValueError("检索类型必须是1（新闻）或2（学术文献）")
        
        if self.search_type == 1:
            if self.search_fields is not None and self.search_fields not in [0, 1]:
                raise ValueError("搜索字段必须是0（正文）或1（标题）")
            
            if self.sort_field is not None and self.sort_field not in [0, 1]:
                raise ValueError("排序方式必须是0（时间）或1（相关度）")
        
        if self.browser_type not in ["chrome", "edge"]:
            raise ValueError("浏览器类型必须是chrome或edge")


class XinhuaSearchResult(BaseModel):
    """新华网搜索结果"""
    
    global_index: int = Field(..., description="全局索引")
    page: int = Field(..., description="所在页码")
    index: int = Field(..., description="页内索引")
    title: str = Field(..., description="标题")
    url: str = Field(..., description="链接")
    summary: str = Field("", description="摘要")
    time: str = Field("", description="发布时间")
    source: str = Field("", description="来源")
