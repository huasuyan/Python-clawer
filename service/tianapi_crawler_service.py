"""
天行数据API爬虫服务
"""
import requests
from typing import List, Dict
from entity.crawler_request import NewsItem


class TianApiCrawlerService:
    """天行数据API爬虫服务"""
    
    def __init__(self, api_key: str):
        """
        初始化服务
        
        参数:
            api_key: 天行数据API密钥
        """
        self.api_key = api_key
        self.apis = {
            "综合": "https://apis.tianapi.com/generalnews/index",
            "社会": "https://apis.tianapi.com/social/index"
        }
    
    def fetch_news(self, source: str, word: str, page: int, num: int = 5) -> Dict:
        """
        获取新闻数据

        参数:
            source: 数据源（综合/社会）
            word: 检索关键词
            page: 页码
            num: 返回数量（固定50）

        返回:
            API响应数据
        """
        if source not in self.apis:
            raise ValueError(f"不支持的数据源: {source}")

        api_url = self.apis[source]

        # 使用form-data格式
        data = {
            "key": self.api_key,
            "word": word,
            "num": num,
            "page": page,
            "form": 1
        }

        try:
            print(f"请求 {source} API: page={page}, word={word}")
            # 使用data参数发送form-data格式
            response = requests.post(api_url, data=data, timeout=10)
            result = response.json()

            if result.get("code") == 200:
                return result
            else:
                print(f"API返回错误: {result.get('msg')}")
                return None

        except Exception as e:
            print(f"请求失败: {e}")
            return None
    
    def parse_news_item(self, item: Dict, source_name: str) -> NewsItem:
        """
        解析新闻条目
        
        参数:
            item: API返回的新闻条目
            source_name: 数据源名称
        
        返回:
            NewsItem对象
        """
        return NewsItem(
            title=item.get("title", ""),
            content=item.get("description", "") or item.get("content", ""),
            publishTime=item.get("ctime", "") or item.get("pubTime", ""),
            source=item.get("source", source_name),
            url=item.get("url", ""),
            picUrl=item.get("picUrl", "") or item.get("pic", "")
        )
    
    def crawl_integration(self, key_word: str, sources: List[str], page: int) -> List[NewsItem]:
        """
        整合爬取多个数据源
        
        参数:
            key_word: 检索关键词
            sources: 数据源列表
            page: 获取多少页的内容
        
        返回:
            新闻列表
        """
        all_news = []
        
        print(f"开始爬取: 关键词={key_word}, 数据源={sources}, 页数={page}")
        print("=" * 80)
        
        for source in sources:
            if source not in self.apis:
                print(f"跳过不支持的数据源: {source}")
                continue
            
            print(f"\n爬取数据源: {source}")
            print("-" * 80)
            
            current_page = 1
            source_total = 0
            
            while current_page <= page:
                print(f"  第 {current_page} 页...")
                
                # 固定num=50
                result = self.fetch_news(source, key_word, current_page)
                
                if not result:
                    print(f"  第 {current_page} 页获取失败，停止该数据源")
                    break
                
                # 解析数据 - 处理不同的返回格式
                # 综合新闻：result.newslist
                # 社会新闻：result.list
                result_data = result.get("result", {})
                news_list = result_data.get("newslist") or result_data.get("list", [])

                if not news_list:
                    print(f"  第 {current_page} 页无数据，停止该数据源")
                    break
                
                # 转换为NewsItem
                for item in news_list:
                    news_item = self.parse_news_item(item, source)
                    all_news.append(news_item)
                
                source_total += len(news_list)
                print(f"  第 {current_page} 页获取 {len(news_list)} 条数据")
                
                # 如果返回数量不足10，说明没有更多数据了
                if len(news_list) < 10:
                    print(f"  返回数量不足50条，停止该数据源")
                    break
                
                current_page += 1
            
            print(f"{source} 数据源共获取 {source_total} 条数据")
        
        print("\n" + "=" * 80)
        print(f"爬取完成！共获取 {len(all_news)} 条数据")
        
        return all_news
