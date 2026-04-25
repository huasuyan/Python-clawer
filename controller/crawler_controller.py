from fastapi import APIRouter, HTTPException, Depends

from common.result import Result
from entity.crawler_model import SpecialReportSetting, SpecialAlertSetting, NewsData, ClearData
from entity.crawler_request import CrawlerIntegrationRequest
from service.tianapi_crawler_service import TianApiCrawlerService
from service.ai_service import AIService
from service.report_generation_service import ReportGenerationService
from config.settings import settings
from config.db import get_db
from sqlalchemy.orm import Session
from datetime import datetime

from utils.tools import merge_unique_news, list_intersect

router = APIRouter(prefix="/api/python/crawler", tags=["爬虫接口"])

# 创建服务实例
crawler_service = None
ai_service = None


def get_crawler_service():
    """获取爬虫服务实例"""
    global crawler_service
    if crawler_service is None:
        if not settings.TIANAPI_KEY:
            print("请配置天行数据API！")
            raise HTTPException(status_code=500, detail="天行数据API密钥未配置")
        crawler_service = TianApiCrawlerService(api_key=settings.TIANAPI_KEY)
    return crawler_service


def get_ai_service():
    """获取AI服务实例"""
    global ai_service
    if ai_service is None:
        if not settings.QWEN_API_KEY:
            print("请配置通义千问API密钥！")
            raise HTTPException(status_code=500, detail="通义千问API密钥未配置")
        ai_service = AIService(api_key=settings.QWEN_API_KEY)
    return ai_service


def filter_news_by_time(news_list: list, filter_time_str: str) -> list:
    """
    根据时间过滤新闻列表

    参数:
        news_list: 新闻列表
        filter_time_str: 过滤时间字符串，格式：YYYY-MM-DD HH:MM:SS

    返回:
        过滤后的新闻列表
    """
    if not filter_time_str:
        return news_list

    try:
        filter_time = datetime.strptime(filter_time_str, "%Y-%m-%d %H:%M:%S")
        filtered_list = []

        for news in news_list:
            publish_time = news.get("publishTime")

            # 如果没有发布时间，保留
            if not publish_time:
                filtered_list.append(news)
                continue

            # 转换发布时间
            if isinstance(publish_time, str):
                try:
                    news_time = datetime.strptime(publish_time, "%Y-%m-%d %H:%M:%S")
                except:
                    try:
                        news_time = datetime.strptime(publish_time.split()[0] + " 00:00:00", "%Y-%m-%d %H:%M:%S")
                    except:
                        filtered_list.append(news)
                        continue
            elif isinstance(publish_time, datetime):
                news_time = publish_time
            else:
                filtered_list.append(news)
                continue

            # 只保留晚于filter_time的新闻
            if news_time > filter_time:
                filtered_list.append(news)

        print(f"时间过滤：原始{len(news_list)}条，过滤后{len(filtered_list)}条")
        return filtered_list

    except Exception as e:
        print(f"时间过滤失败: {e}")
        return news_list


def save_news_to_database(enriched_data_list: list, db: Session) -> list:
    """
    保存新闻数据到数据库

    参数:
        enriched_data_list: AI补全后的新闻数据列表
        db: 数据库会话

    返回:
        保存后的新闻ID列表
    """
    news_ids = []

    for data in enriched_data_list:
        try:
            # 创建NewsData对象
            news_record = NewsData(
                special_report_id=data.get("special_report_id") if data.get("special_report_id") is not None else 0,
                is_report_need=data.get("is_report_need") if data.get("is_report_need") is not None else 0,
                alert_id=data.get("alert_id") if data.get("alert_id") is not None else 0,
                title=data.get("title"),
                content=data.get("content"),
                video=data.get("video"),
                platform=data.get("platform"),
                source=data.get("source"),
                publisher=data.get("publisher"),
                publish_time=data.get("publish_time"),
                comment=data.get("comment"),
                region=data.get("region"),
                original_url=data.get("original_url"),
                article_type=data.get("article_type"),
                source_url=data.get("source_url")
            )

            db.add(news_record)
            db.flush()  # 获取news_id
            news_ids.append(news_record.news_id)

        except Exception as e:
            print(f"保存新闻失败: {e}")
            continue

    db.commit()
    print(f"成功保存{len(news_ids)}条新闻到数据库")

    return news_ids


def clean_and_save_news(news_ids: list, enriched_data_list: list, db: Session):
    """
    使用AI清洗新闻并保存到clear_data表

    参数:
        news_ids: 新闻ID列表
        enriched_data_list: 新闻数据列表
        db: 数据库会话
    """
    try:
        # 准备清洗数据
        news_list_for_clean = []
        for idx, news_id in enumerate(news_ids):
            if idx < len(enriched_data_list):
                news_list_for_clean.append({
                    "news_id": news_id,
                    "title": enriched_data_list[idx].get("title", ""),
                    "content": enriched_data_list[idx].get("content", "")
                })

        # 使用AI清洗
        report_service = ReportGenerationService(ai_service=get_ai_service())
        clean_data_list = report_service.clean_and_label_news(news_list_for_clean)

        # 保存清洗数据
        for clean_data in clean_data_list:
            try:
                clear_record = ClearData(
                    news_id=clean_data["news_id"],
                    sensitivity_level=clean_data["sensitivity_level"],
                    sensitivity_label=clean_data["sensitivity_label"],
                    sentiment_type=clean_data["sentiment_type"]
                )
                db.add(clear_record)
            except Exception as e:
                print(f"保存清洗数据失败: {e}")
                continue

        db.commit()
        print(f"成功保存{len(clean_data_list)}条清洗数据")

    except Exception as e:
        print(f"清洗数据失败: {e}")
        db.rollback()


@router.post("/runIntegration")
async def run_integration(request: CrawlerIntegrationRequest, db: Session = Depends(get_db)):
    """
    整合爬虫接口

    参数说明：
    - task_id: 任务ID（必填）
    - task_way: 任务类型，可选值：report/alert（必填）
    - filter_time:

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

            # 时间过滤（如果提供了filter_time）
            if request.filter_time:
                news_list = filter_news_by_time(news_list, request.filter_time)

                if not news_list:
                    print("时间过滤后无新数据")
                    return Result.success(data=None, msg="无新数据")

            # 使用AI补全数据（单条处理）
            enriched_data_list = []
            for news_dict in news_list:
                url = news_dict.get("url", "")

                # AI补全数据
                enriched_data = ai_service.enrich_news_data(url, news_dict)
                enriched_data["special_report_id"] = request.task_id
                enriched_data["is_report_need"] = 1
                enriched_data["alert_id"] = 0

                enriched_data_list.append(enriched_data)

            # 保存到news_data表
            news_ids = save_news_to_database(enriched_data_list, db)

            # AI清洗并保存到clear_data表
            clean_and_save_news(news_ids, enriched_data_list, db)

            # 返回null而不是数据列表
            return Result.success(data=None, msg=f"成功处理{len(news_ids)}条新闻")

        elif request.task_way == "alert":
            # 查询预警设置
            setting = db.query(SpecialAlertSetting).filter(
                SpecialAlertSetting.alert_id == request.task_id
            ).first()

            if not setting:
                return Result.error(msg="未找到对应的预警设置！")

            # 获取参数和关键词
            params = setting.params
            keywordGroups = setting.key_word.get("keywordGroups")
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

            # 时间过滤（如果提供了filter_time）
            if request.filter_time:
                news_list = filter_news_by_time(news_list, request.filter_time)

                if not news_list:
                    print("时间过滤后无新数据")
                    return Result.success(data=None, msg="无新数据")

            # 使用AI补全数据（单条处理）
            enriched_data_list = []
            for news_dict in news_list:
                url = news_dict.get("url", "")

                # AI补全数据
                enriched_data = ai_service.enrich_news_data(url, news_dict)
                enriched_data["special_report_id"] = 0
                enriched_data["is_report_need"] = 0
                enriched_data["alert_id"] = request.task_id

                enriched_data_list.append(enriched_data)

            # 保存到news_data表
            news_ids = save_news_to_database(enriched_data_list, db)

            # AI清洗并保存到clear_data表
            clean_and_save_news(news_ids, enriched_data_list, db)

            setting.latest_news_time = enriched_data_list[0].publish_time
            db.add(setting)
            db.commit()

            # 返回null而不是数据列表
            return Result.success(data=None, msg=f"成功处理{len(news_ids)}条新闻")

        else:
            return Result.error(f"无法识别的任务类型：{request.task_way}!")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"爬取失败: {str(e)}")

@router.get("")

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
