from fastapi import APIRouter, HTTPException
from typing import List
from entity.xinhua_search_request import XinhuaSearchRequest, XinhuaSearchResult
from service.xinhua_search_service import XinhuaSearchService
from common.result import Result

router = APIRouter(prefix="/api/xinhua", tags=["新华网搜索"])

# 创建服务实例
xinhua_service = XinhuaSearchService()


@router.post("/search")
async def search_xinhua(request: XinhuaSearchRequest):
    """
    新华网搜索接口

    参数说明：
    - keyword: 搜索关键词（必填）
    - search_type: 检索类型，1=新闻，2=学术文献（默认1）
    - search_fields: 搜索字段（仅search_type=1时有效），0=正文，1=标题
    - sort_field: 排序方式（仅search_type=1时有效），0=时间，1=相关度
    - start_page: 起始页码，从0开始（0表示第1页，默认0）
    - end_page: 结束页码，包含（0表示第1页，默认0）
    - browser_type: 浏览器类型，chrome或edge（默认chrome）

    注意：分页是通过在页面上点击翻页按钮实现的，不是通过URL参数

    示例：
    {
        "keyword": "科技",
        "search_type": 1,
        "search_fields": 1,
        "sort_field": 0,
        "start_page": 0,
        "end_page": 2,
        "browser_type": "chrome"
    }

    这将抓取第1页到第3页的内容
    """
    try:
        results = xinhua_service.search(request)
        
        return Result.success(
            data=[result.model_dump() for result in results],
            msg=f"成功获取 {len(results)} 条搜索结果"
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/test")
async def test_xinhua():
    """测试接口"""
    return Result.success(msg="新华网搜索服务运行正常")
