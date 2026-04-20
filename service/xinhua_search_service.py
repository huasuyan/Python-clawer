from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import random
from typing import List, Dict
from urllib.parse import quote
from entity.xinhua_search_request import XinhuaSearchRequest, XinhuaSearchResult


class XinhuaSearchService:
    """新华网搜索爬虫服务"""

    def __init__(self):
        self.wait_time = 5  # 页面加载等待时间（秒）
        self.page_delay = 3  # 页面之间的延迟时间（秒）

        # 随机User-Agent列表
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        ]
    
    def _build_url(self, search_type: int, keyword: str, search_fields: str, sort_field: str) -> str:
        """构建搜索URL，对关键词进行URL编码"""
        encoded_keyword = quote(keyword)
        return f"https://so.news.cn/#search/{search_type}/{encoded_keyword}/{search_fields}/{sort_field}"
    
    def _create_driver(self, browser_type: str):
        """创建浏览器驱动，增强反检测能力"""
        # 随机选择User-Agent
        user_agent = random.choice(self.user_agents)

        if browser_type.lower() == "chrome":
            options = ChromeOptions()

            # 基础选项
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-software-rasterizer')

            # 反检测选项
            options.add_argument(f'--user-agent={user_agent}')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            # 添加更多浏览器特征
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins-discovery')
            options.add_argument('--start-maximized')

            # 语言设置
            options.add_argument('--lang=zh-CN')
            options.add_experimental_option('prefs', {
                'intl.accept_languages': 'zh-CN,zh;q=0.9,en;q=0.8'
            })

            driver = webdriver.Chrome(options=options)

            # 执行CDP命令隐藏webdriver特征
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": user_agent
            })
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            return driver

        elif browser_type.lower() == "edge":
            options = EdgeOptions()

            # 基础选项
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')

            # 反检测选项
            options.add_argument(f'--user-agent={user_agent}')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            # 添加更多浏览器特征
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-extensions')
            options.add_argument('--start-maximized')

            # 语言设置
            options.add_argument('--lang=zh-CN')

            driver = webdriver.Edge(options=options)

            # 执行CDP命令隐藏webdriver特征
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": user_agent
            })
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            return driver

        else:
            raise ValueError(f"不支持的浏览器类型: {browser_type}")
    
    def _fetch_page_html(self, url: str, browser_type: str, page_num: int) -> str:
        """
        获取指定页码的HTML内容

        参数:
            url: 基础URL
            browser_type: 浏览器类型
            page_num: 页码（从1开始，1表示第一页）
        """
        driver = None
        try:
            driver = self._create_driver(browser_type)
            driver.set_page_load_timeout(30)

            # 添加随机延迟，模拟人类行为
            time.sleep(random.uniform(1, 3))

            driver.get(url)

            # 随机滚动页面，模拟人类浏览
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
            time.sleep(random.uniform(0.5, 1.5))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(random.uniform(0.5, 1.5))

            # 等待页面初始加载
            time.sleep(self.wait_time + random.uniform(0, 2))

            # 如果不是第一页，需要点击翻页
            if page_num > 1:
                for current_page in range(2, page_num + 1):
                    try:
                        print(f"  正在翻到第 {current_page} 页...")

                        # 随机延迟
                        time.sleep(random.uniform(2, 4))

                        # 滚动到页面底部（分页通常在底部）
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(random.uniform(1, 2))

                        # 方法1: 尝试找到并点击"下一页"按钮
                        try:
                            next_button = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'next') or contains(text(), '下一页')]"))
                            )
                            # 模拟鼠标移动到按钮
                            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                            time.sleep(random.uniform(0.5, 1))
                            driver.execute_script("arguments[0].click();", next_button)
                            time.sleep(self.wait_time + random.uniform(1, 3))
                            continue
                        except:
                            pass

                        # 方法2: 尝试找到页码按钮直接点击
                        try:
                            page_button = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, f"//button[text()='{current_page}' or @data-page='{current_page}']"))
                            )
                            driver.execute_script("arguments[0].scrollIntoView(true);", page_button)
                            time.sleep(random.uniform(0.5, 1))
                            driver.execute_script("arguments[0].click();", page_button)
                            time.sleep(self.wait_time + random.uniform(1, 3))
                            continue
                        except:
                            pass

                        # 方法3: 尝试通过分页组件的class查找
                        try:
                            pagination = driver.find_element(By.CLASS_NAME, "ant-pagination")
                            page_items = pagination.find_elements(By.TAG_NAME, "li")
                            for item in page_items:
                                if item.text == str(current_page):
                                    driver.execute_script("arguments[0].scrollIntoView(true);", item)
                                    time.sleep(random.uniform(0.5, 1))
                                    driver.execute_script("arguments[0].click();", item)
                                    time.sleep(self.wait_time + random.uniform(1, 3))
                                    break
                            continue
                        except:
                            pass

                        print(f"  警告: 无法翻到第 {current_page} 页，可能已到最后一页")
                        break

                    except Exception as e:
                        print(f"  翻页失败: {e}")
                        break

            # 最后再随机滚动一下
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(random.uniform(0.5, 1))

            # 获取当前页面的HTML
            html_content = driver.page_source
            return html_content

        except Exception as e:
            print(f"获取页面失败: {e}")
            raise

        finally:
            if driver:
                driver.quit()
    
    def _parse_html(self, html_content: str) -> List[Dict]:
        """解析HTML内容，提取搜索结果"""
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []
        
        # 查找所有新闻链接
        links = soup.find_all('a', href=True)
        news_links = [link for link in links if 'news.cn' in link.get('href', '')]
        
        for idx, link in enumerate(news_links[:20], 1):  # 限制每页最多20条
            href = link.get('href', '')
            title = link.get_text(strip=True)
            
            # 过滤掉太短的标题
            if title and len(title) > 5:
                result = {
                    'index': idx,
                    'title': title,
                    'url': href,
                    'summary': '',
                    'time': '',
                    'source': ''
                }
                results.append(result)
        
        return results
    
    def search(self, request: XinhuaSearchRequest) -> List[XinhuaSearchResult]:
        """
        执行搜索

        参数:
            request: 搜索请求参数

        返回:
            搜索结果列表
        """
        # 验证参数
        request.validate_params()

        all_results = []
        total_pages = request.end_page - request.start_page + 1

        print(f"开始抓取新华网搜索结果")
        print(f"关键词: {request.keyword}")
        print(f"检索类型: {'新闻' if request.search_type == 1 else '学术文献'}")
        print(f"页数范围: 第{request.start_page + 1}页到第{request.end_page + 1}页（共{total_pages}页）")
        print(f"浏览器: {request.browser_type}")
        print("=" * 80)

        # 构建基础URL（只访问一次）
        url = self._build_url(
            request.search_type,
            request.keyword,
            request.get_search_fields_value(),
            request.get_sort_field_value()
        )

        print(f"URL: {url}")

        for page_index in range(request.start_page, request.end_page + 1):
            page_num = page_index + 1  # 页码从1开始显示
            print(f"\n正在抓取第 {page_num} 页...")

            try:
                # 获取指定页码的HTML
                html_content = self._fetch_page_html(url, request.browser_type, page_num)

                # 解析结果
                page_results = self._parse_html(html_content)

                # 添加页码和全局索引
                for result in page_results:
                    result['page'] = page_index
                    result['global_index'] = len(all_results) + 1
                    all_results.append(XinhuaSearchResult(**result))

                print(f"第 {page_num} 页提取到 {len(page_results)} 条结果")

                # 页面之间随机延迟（除了最后一页）
                if page_index < request.end_page:
                    delay = random.uniform(self.page_delay, self.page_delay + 3)
                    print(f"等待{delay:.1f}秒后继续...")
                    time.sleep(delay)

            except Exception as e:
                print(f"第 {page_num} 页抓取失败: {e}")
                continue

        print("\n" + "=" * 80)
        print(f"抓取完成！共获取 {len(all_results)} 条结果")

        return all_results
