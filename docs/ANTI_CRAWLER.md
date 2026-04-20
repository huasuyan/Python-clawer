# 反爬虫策略说明

## 问题：被新华网限制访问

如果遇到"请求被限制"的问题，说明触发了网站的反爬虫机制。

## 已实施的反爬虫措施

### 1. 隐藏Selenium特征
- 禁用自动化控制标识 `--disable-blink-features=AutomationControlled`
- 移除automation扩展
- 覆盖navigator.webdriver属性
- 使用CDP命令修改User-Agent

### 2. 随机化User-Agent
- 内置8个不同的真实浏览器User-Agent
- 每次请求随机选择

### 3. 模拟人类行为
- 访问页面前随机延迟1-3秒
- 页面加载后随机滚动
- 翻页前滚动到底部
- 点击前移动到元素位置
- 页面之间随机延迟3-6秒

### 4. 浏览器指纹优化
- 设置真实的窗口大小
- 添加语言偏好设置
- 禁用插件发现
- 最大化窗口

## 额外建议

### 方案1: 增加延迟时间

修改 `config/crawler_config.py`:

```python
PAGE_LOAD_WAIT = 8  # 增加到8秒
PAGE_DELAY_MIN = 5  # 最小延迟5秒
PAGE_DELAY_MAX = 10  # 最大延迟10秒
```

### 方案2: 使用代理IP

如果仍然被限制，可以添加代理支持：

```python
# 在_create_driver方法中添加
options.add_argument('--proxy-server=http://your-proxy:port')
```

推荐代理服务：
- 快代理
- 阿布云
- 芝麻代理

### 方案3: 减少抓取频率

- 一次只抓取1-2页
- 每次抓取后等待更长时间（10-30分钟）
- 分批次抓取

### 方案4: 更换IP地址

临时解决方案：
1. 重启路由器获取新IP
2. 使用VPN
3. 使用移动网络热点

### 方案5: 使用Cookie和Session

如果有新华网账号，可以添加登录Cookie：

```python
driver.get("https://so.news.cn")
driver.add_cookie({
    'name': 'cookie_name',
    'value': 'cookie_value',
    'domain': '.news.cn'
})
```

### 方案6: 非无头模式测试

临时关闭无头模式，观察是否被检测：

修改 `service/xinhua_search_service.py`，注释掉：
```python
# options.add_argument('--headless')  # 暂时关闭无头模式
```

### 方案7: 使用Undetected ChromeDriver

安装增强版驱动：
```bash
pip install undetected-chromedriver
```

修改代码使用：
```python
import undetected_chromedriver as uc
driver = uc.Chrome(options=options)
```

## 当前配置调整

### 立即生效的调整

1. **增加延迟**（推荐）
```bash
# 编辑 config/crawler_config.py
PAGE_DELAY_MIN = 10  # 改为10秒
PAGE_DELAY_MAX = 15  # 改为15秒
```

2. **减少抓取页数**
```json
{
  "start_page": 0,
  "end_page": 0  // 只抓取1页
}
```

3. **等待一段时间**
- 停止抓取30分钟-1小时
- 更换网络环境
- 清除浏览器缓存

## 检测是否被封禁

运行测试脚本：

```bash
python test_api.py
```

如果返回：
- 403/429错误 → IP被限制
- 空白页面 → 可能被检测为机器人
- 验证码页面 → 需要人工验证

## 长期解决方案

1. **使用代理池** - 轮换IP地址
2. **分布式爬取** - 多台机器分担请求
3. **降低频率** - 每天固定时间少量抓取
4. **寻找API接口** - 直接调用后端API（推荐）

## 紧急恢复步骤

如果当前IP被封：

1. 停止所有爬虫程序
2. 等待24小时
3. 更换IP地址
4. 使用最保守的配置重新开始
5. 每次只抓取1页
6. 页面间隔至少30秒

## 联系方式

如果问题持续，可以考虑：
- 联系新华网申请API权限
- 使用官方提供的数据接口
- 购买商业数据服务
