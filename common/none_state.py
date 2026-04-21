from enum import IntEnum

class CrawlerNoneTaskState(IntEnum):
    """爬虫任务状态枚举"""
    FAILED = -1       # 检索失败
    CREATED = 0       # 检索任务已创建
    CRAWLING = 1      # 爬取数据中
    CLEANING = 2      # 数据清洗中
    SAVING = 3        # 数据保存中
    FINISHED = 4      # 检索任务已完成

# 额外加：数字转中文描述的字典
NONE_STATE_TEXT = {
    -1: "检索失败",
    0: "检索任务已创建",
    1: "爬取数据中",
    2: "数据清洗中",
    3: "数据保存中",
    4: "检索任务已完成"
}