"""
新华网爬虫反爬虫配置
"""

# 基础延迟配置（秒）
PAGE_LOAD_WAIT = 5  # 页面加载等待时间
PAGE_DELAY_MIN = 3  # 页面之间最小延迟
PAGE_DELAY_MAX = 6  # 页面之间最大延迟

# 随机延迟范围（秒）
RANDOM_DELAY_MIN = 1  # 随机延迟最小值
RANDOM_DELAY_MAX = 3  # 随机延迟最大值

# 滚动延迟（秒）
SCROLL_DELAY_MIN = 0.5
SCROLL_DELAY_MAX = 1.5

# User-Agent列表（会随机选择）
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
]

# 浏览器窗口大小
WINDOW_SIZES = [
    (1920, 1080),
    (1366, 768),
    (1440, 900),
    (1536, 864),
]

# 是否启用反检测功能
ENABLE_ANTI_DETECTION = True

# 是否模拟人类行为（滚动、随机延迟等）
ENABLE_HUMAN_BEHAVIOR = True

# 最大重试次数
MAX_RETRIES = 3

# 请求超时时间（秒）
REQUEST_TIMEOUT = 30
