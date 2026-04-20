# 新华网搜索API使用说明

## 功能概述

新华网搜索爬虫服务，支持在新闻和学术文献中搜索内容，可自定义搜索字段、排序方式，支持多页抓取。

## 技术特点

- 支持Chrome和Edge两种浏览器
- 支持Windows和Linux系统
- 使用Selenium进行动态页面渲染
- 自动解析搜索结果
- 支持多页批量抓取

## API接口

### 1. 搜索接口

**接口地址**: `POST /api/xinhua/search`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 | 默认值 |
|--------|------|------|------|--------|
| keyword | string | 是 | 搜索关键词 | - |
| search_type | int | 否 | 检索类型：1=新闻，2=学术文献 | 1 |
| search_fields | int | 否 | 搜索字段（仅search_type=1时有效）：0=正文，1=标题 | null |
| sort_field | int | 否 | 排序方式（仅search_type=1时有效）：0=时间，1=相关度 | null |
| start_page | int | 否 | 起始页码（从0开始） | 0 |
| end_page | int | 否 | 结束页码（包含） | 0 |
| browser_type | string | 否 | 浏览器类型：chrome 或 edge | chrome |

**请求示例**:

```json
{
  "keyword": "科技",
  "search_type": 1,
  "search_fields": 1,
  "sort_field": 0,
  "start_page": 0,
  "end_page": 2,
  "browser_type": "chrome"
}
```

**响应示例**:

```json
{
  "code": 200,
  "msg": "成功获取 60 条搜索结果",
  "data": [
    {
      "global_index": 1,
      "page": 0,
      "index": 1,
      "title": "科技创新推动高质量发展",
      "url": "https://www.news.cn/xxx",
      "summary": "",
      "time": "",
      "source": ""
    }
  ]
}
```

### 2. 测试接口

**接口地址**: `GET /api/xinhua/test`

**响应示例**:

```json
{
  "code": 200,
  "msg": "新华网搜索服务运行正常",
  "data": null
}
```

## 参数说明

### search_type（检索类型）

- `1`: 在新闻中检索
- `2`: 在学术文献中检索

### search_fields（搜索字段，仅search_type=1时有效）

- `0`: 在正文中检索
- `1`: 在标题中检索

### sort_field（排序方式，仅search_type=1时有效）

- `0`: 按时间排序
- `1`: 按相关度排序

### browser_type（浏览器类型）

- `chrome`: 使用Chrome浏览器（推荐Linux服务器使用）
- `edge`: 使用Edge浏览器（默认，推荐Windows使用）

## 使用示例

### Python调用示例

```python
import requests

url = "http://localhost:8088/api/xinhua/search"

# 示例1: 在新闻标题中搜索"科技"，按时间排序，抓取3页
data = {
    "keyword": "科技",
    "search_type": 1,
    "search_fields": 1,
    "sort_field": 0,
    "start_page": 0,
    "end_page": 2,
    "browser_type": "chrome"
}

response = requests.post(url, json=data)
result = response.json()

print(f"获取到 {len(result['data'])} 条结果")
for item in result['data'][:5]:
    print(f"{item['title']} - {item['url']}")
```

### curl调用示例

```bash
curl -X POST "http://localhost:8088/api/xinhua/search" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "人工智能",
    "search_type": 1,
    "search_fields": 1,
    "sort_field": 0,
    "start_page": 0,
    "end_page": 1,
    "browser_type": "chrome"
  }'
```

## 部署说明

### Windows部署

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 确保已安装Chrome或Edge浏览器

3. 启动服务：
```bash
python main.py
```

### Linux部署

1. 安装Chrome浏览器：
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y wget gnupg
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
sudo apt update
sudo apt install -y google-chrome-stable
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 启动服务：
```bash
python main.py
```

## 注意事项

1. 每页之间会自动延迟3秒，避免请求过快
2. 页面加载等待时间为5秒，确保JavaScript完全执行
3. 每页最多返回20条结果
4. 建议使用Chrome浏览器，兼容性更好
5. Linux服务器必须使用无头模式（已自动配置）

## 测试

运行测试脚本：

```bash
python test_xinhua_service.py
```

## API文档

启动服务后访问：`http://localhost:8088/docs`
