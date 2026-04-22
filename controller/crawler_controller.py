import json
import logging

from fastapi import APIRouter, HTTPException, Depends

from common.crawler_state import CrawlerNoneTaskState, NONE_STATE_TEXT, CrawlerCronTaskState, CRON_STATE_TEXT
from common.result import Result
from entity.crawler_model import CrawlerNone, CrawlerCron, SpecialReportSetting, SpecialAlertSetting
from entity.crawler_request import CrawlerIntegrationRequest
from service.tianapi_crawler_service import TianApiCrawlerService
from service.ai_service import AIService
from config.settings import settings
from config.db import get_db
from sqlalchemy.orm import Session

from utils.tools import merge_unique_news, list_intersect
from websocketClient.java_client import java_ws

router = APIRouter(prefix="/api/python/crawler", tags=["爬虫接口"])

# 创建服务实例
crawler_service = None
ai_service = None


def get_crawler_service():
    """获取爬虫服务实例"""
    global crawler_service
    if crawler_service is None:
        if not settings.TIANAPI_KEY:
            logging.error("请配置天行数据API！")
            raise HTTPException(status_code=500, detail="天行数据API密钥未配置")
        crawler_service = TianApiCrawlerService(api_key=settings.TIANAPI_KEY)
    return crawler_service


def get_ai_service():
    """获取AI服务实例"""
    global ai_service
    if ai_service is None:
        if not settings.QWEN_API_KEY:
            logging.error("请配置通义千问API密钥！")
            raise HTTPException(status_code=500, detail="通义千问API密钥未配置")
        ai_service = AIService(api_key=settings.QWEN_API_KEY)
    return ai_service


@router.post("/runIntegration")
async def run_integration(request: CrawlerIntegrationRequest, db: Session = Depends(get_db)):
    """
    整合爬虫接口

    参数说明：
    - task_id: 任务ID（必填）
    - task_way: 任务类型，可选值：report/alert（必填）

    说明：
    - task_way为report时，访问special_report_setting表
    - task_way为alert时，访问special_alert_setting表
    - 使用AI补全新闻数据的所有字段

    示例：
    {
        "task_id": 1,
        "task_way": "report"
    }

    返回格式：
    {
        "code": 1,
        "msg": "success",
        "data": {
            "dataList": [...]
        }
    }
    """
    try:
        # 获取服务实例
        service = get_crawler_service()
        ai_service = get_ai_service()

        if request.task_way == "report":
            # 查询专题报告设置
            setting = db.query(SpecialReportSetting).filter(
                SpecialReportSetting.special_report_id == request.task_id
            ).first()

            if not setting:
                return Result.error(msg="未找到对应的专题报告设置！")

            # 获取参数和关键词
            params = setting.params
            keywordGroups = setting.monitor_keywords.get("keywordGroups")
            sources = params.get("sources", ["综合"])
            page = params.get("page", 1)

            # 遍历分组 + 遍历每个关键词
            last_lists = []
            for group in keywordGroups:
                # 遍历爬取组内的每个词，将搜索结果合并
                cur_lists = []
                for word in group:
                    get_news_list = service.crawl_integration(
                        key_word=word,
                        sources=sources,
                        page=page
                    )
                    # 转换为字典列表
                    clear_news_list = [news.model_dump() for news in get_news_list]
                    cur_lists.append(clear_news_list)
                last_lists.append(merge_unique_news(cur_lists))

            news_list = list_intersect(last_lists)

            # 使用AI补全数据
            i = 1
            enriched_data_list = []
            for news in news_list:
                news_dict = news.model_dump() if hasattr(news, 'model_dump') else news
                url = news_dict.get("url", "")

                # AI补全数据
                print(f"正在补全第{i}条数据，补全前数据为{news_dict}")
                enriched_data = ai_service.enrich_news_data(url, news_dict)
                enriched_data["special_report_id"] = request.task_id
                enriched_data["alert_id"] = None
                print(f"第{i}条数据补全完成，补全后数据为{enriched_data}")
                i = i + 1


                enriched_data_list.append(enriched_data)

            return Result.successDataList(dataList=enriched_data_list)

        elif request.task_way == "alert":
            # 查询预警设置
            setting = db.query(SpecialAlertSetting).filter(
                SpecialAlertSetting.alert_id == request.task_id
            ).first()

            if not setting:
                return Result.error(msg="未找到对应的预警设置！")

            # 获取参数和关键词
            params = setting.params
            keywords = setting.key_word
            sources = params.get("sources", ["综合"])
            page = params.get("page", 1)

            # 执行爬取 - 处理关键词组
            news_list = []
            if isinstance(keywords, dict) and "keywordGroups" in keywords:
                # 关键词组逻辑
                keywordGroups = keywords.get("keywordGroups", [])
                last_lists = []

                for group in keywordGroups:
                    cur_lists = []
                    for word in group:
                        get_news_list = service.crawl_integration(
                            key_word=word,
                            sources=sources,
                            page=page
                        )
                        clear_news_list = [news.model_dump() for news in get_news_list]
                        cur_lists.append(clear_news_list)
                    last_lists.append(merge_unique_news(cur_lists))

                news_list = list_intersect(last_lists)
            elif isinstance(keywords, list):
                # 简单关键词列表
                for keyword in keywords:
                    crawled_news = service.crawl_integration(
                        key_word=keyword,
                        sources=sources,
                        page=page
                    )
                    news_list.extend([news.model_dump() for news in crawled_news])
            else:
                # 单个关键词
                crawled_news = service.crawl_integration(
                    key_word=str(keywords),
                    sources=sources,
                    page=page
                )
                news_list = [news.model_dump() for news in crawled_news]

            # 使用AI补全数据
            enriched_data_list = []
            for news_dict in news_list:
                url = news_dict.get("url", "")

                # AI补全数据
                enriched_data = ai_service.enrich_news_data(url, news_dict)
                enriched_data["special_report_id"] = None
                enriched_data["alert_id"] = request.task_id

                enriched_data_list.append(enriched_data)

            return Result.successDataList(dataList=enriched_data_list)

        elif request.task_way == "none":
            # 获取爬虫信息
            crawlerInfo = db.query(CrawlerNone).filter(CrawlerNone.crawler_id == request.task_id).first()
            if not crawlerInfo:
                return Result.error(msg="未找到对应手动检索任务！")

            if crawlerInfo.state != CrawlerNoneTaskState.CREATED :
                return Result.error(msg=f"手动检索任务状态错误：要求状态为{NONE_STATE_TEXT[CrawlerNoneTaskState.CREATED]},当前状态为：{NONE_STATE_TEXT[crawlerInfo.state]}！")

            # 读取参数
            params_dict = crawlerInfo.params
            sources = list(params_dict.get("sources"))
            page = int(params_dict.get("page"))

            # 设置爬取状态
            crawler_old_state = crawlerInfo.state
            crawlerInfo.state = CrawlerNoneTaskState.CRAWLING
            db.add(crawlerInfo)
            db.commit()

            # websocket给java发消息
            ws_msg = {
                "type": "crawler_none_state_change",
                "user_id": crawlerInfo.user_id,
                "crawler_id": request.task_id,
                "crawler_name": crawlerInfo.crawler_name,
                "crawler_old_state": NONE_STATE_TEXT[crawler_old_state],
                "crawler_new_state": NONE_STATE_TEXT[CrawlerNoneTaskState.CRAWLING]
            }
            await java_ws.send(ws_msg)

            # 执行爬取
            news_list = service.crawl_integration(
                key_word=crawlerInfo.key_word,
                sources=sources,
                page=page
            )

            # 设置爬取状态
            crawler_old_state = CrawlerNoneTaskState.CRAWLING
            crawlerInfo.state = CrawlerNoneTaskState.CLEANING
            db.add(crawlerInfo)
            db.commit()

            # websocket给java发消息
            ws_msg = {
                "type": "crawler_none_state_change",
                "user_id": crawlerInfo.user_id,
                "crawler_id": request.task_id,
                "crawler_name": crawlerInfo.crawler_name,
                "crawler_old_state": NONE_STATE_TEXT[crawler_old_state],
                "crawler_new_state": NONE_STATE_TEXT[CrawlerNoneTaskState.CLEANING]
            }
            await java_ws.send(ws_msg)

            # 转换为字典列表
            data_list = [news.model_dump() for news in news_list]

            # 返回结果
            return Result.successDataList(dataList=data_list)

        elif request.task_way == "cron":
            # 获取爬虫信息
            crawlerInfo = db.query(CrawlerCron).filter(CrawlerCron.crawler_id == request.task_id).first()
            if not crawlerInfo:
                return Result.error(msg="未找到对应舆情预警任务！")

            if crawlerInfo.state != CrawlerCronTaskState.WAITTING and crawlerInfo.state != CrawlerCronTaskState.FAILED:
                return Result.error(msg=f"舆情预警任务状态错误：要求状态为{CRON_STATE_TEXT[CrawlerCronTaskState.WAITTING]}/{CRON_STATE_TEXT[CrawlerCronTaskState.FAILED]},当前状态为：{CRON_STATE_TEXT[crawlerInfo.state]}！")

            # 读取参数
            params_dict = crawlerInfo.params
            sources = list(params_dict.get("sources"))
            page = int(params_dict.get("page"))

            # 设置爬取状态
            crawler_old_state = crawlerInfo.state
            crawlerInfo.state = CrawlerCronTaskState.CRAWLING
            db.add(crawlerInfo)
            db.commit()

            # websocket给java发消息
            ws_msg = {
                "type": "crawler_cron_state_change",
                "user_id": crawlerInfo.user_id,
                "crawler_id": request.task_id,
                "crawler_name": crawlerInfo.crawler_name,
                "crawler_old_state": CRON_STATE_TEXT[crawler_old_state],
                "crawler_new_state": CRON_STATE_TEXT[CrawlerCronTaskState.CRAWLING]
            }
            await java_ws.send(ws_msg)

            # 执行爬取
            keyword = crawlerInfo.key_word
            keywordGroups = keyword.get("keywordGroups")

            # 遍历分组 + 遍历每个关键词
            last_lists = []
            for group in keywordGroups:
                # 遍历爬取组内的每个词，将搜索结果合并
                cur_lists = []
                for word in group:
                    get_news_list = service.crawl_integration(
                        key_word=word,
                        sources=sources,
                        page=page
                    )
                    # 转换为字典列表
                    clear_news_list = [news.model_dump() for news in get_news_list]
                    cur_lists.append(clear_news_list)
                last_lists.append(merge_unique_news(cur_lists))

            news_list = list_intersect(last_lists)

            # 设置爬取状态
            crawler_old_state = CrawlerCronTaskState.CRAWLING
            crawlerInfo.state = CrawlerCronTaskState.CLEANING
            db.add(crawlerInfo)
            db.commit()

            # websocket给java发消息
            ws_msg = {
                "type": "crawler_none_state_change",
                "user_id": crawlerInfo.user_id,
                "crawler_id": request.task_id,
                "crawler_name": crawlerInfo.crawler_name,
                "crawler_old_state": CRON_STATE_TEXT[crawler_old_state],
                "crawler_new_state": CRON_STATE_TEXT[CrawlerCronTaskState.CLEANING]
            }
            await java_ws.send(ws_msg)

            # 返回结果
            return Result.successDataList(dataList=news_list)
        else:
            return Result.error(f"无法识别的任务类型：{request.task_way}!")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"爬取失败: {str(e)}")


@router.get("/test")
async def test_crawler():
    """测试接口"""
    return {
        "code": 1,
        "msg": "爬虫服务运行正常",
        "data": {
            "supported_sources": ["综合", "社会"],
            "max_num_per_page": 50
        }
    }
