# Python爬虫项目 - 天行数据API整合

## 项目简介

基于FastAPI的爬虫服务，整合天行数据API，支持多数据源新闻查询。

## 功能特点

- ✅ 支持"综合"和"社会"两个数据源
- ✅ 固定每页50条数据
- ✅ 支持多页查询
- ✅ 智能停止（当返回数量不足50时自动停止）
- ✅ 支持多数据源同时查询
- ✅ 完整的代理池支持（可选）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

复制配置文件：
```bash
cp .env.example .env
```

编辑`.env`文件，填入天行数据API密钥：
```bash
TIANAPI_KEY=your_tianapi_key
```

**获取API密钥**：
1. 注册天行数据：https://www.tianapi.com/
2. 登录后台获取API Key

### 3. 启动服务

```bash
python main.py
```

服务将在 `http://localhost:8088` 启动

### 4. 测试接口

```bash
python test_crawler_api.py
```

## API接口

### 整合爬虫接口

**接口地址**: `POST /api/python/crawler/runIntegration`

**请求参数**:

```json
{
  "key_word": "科技",
  "sources": ["综合", "社会"],
  "page": 2
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| key_word | string | 是 | 检索关键词 |
| sources | array | 是 | 数据源列表，可选值：["综合", "社会"] |
| page | int | 否 | 获取多少页的内容，默认1 |

**返回格式**:

```json
{
  "code": 1,
  "msg": "success",
  "data": {
    "dataList": [
      {
        "title": "新闻标题",
        "content": "新闻内容",
        "publishTime": "2024-01-01 12:00:00",
        "source": "来源",
        "url": "https://...",
        "picUrl": "https://..."
      }
    ]
  }
}
```


### 测试接口

**接口地址**: `GET /api/python/crawler/test`

**返回示例**:

```json
{
  "code": 1,
  "msg": "爬虫服务运行正常",
  "data": {
    "supported_sources": ["综合", "社会"],
    "max_num_per_page": 50
  }
}
```

## 使用示例

### Python调用

```python
import requests

response = requests.post(
    "http://localhost:8088/api/python/crawler/runIntegration",
    json={
        "key_word": "科技",
        "sources": ["综合", "社会"],
        "page": 2
    }
)

result = response.json()
print(f"获取到 {len(result['data']['dataList'])} 条数据")
```

### curl调用

```bash
curl -X POST "http://localhost:8088/api/python/crawler/runIntegration" \
  -H "Content-Type: application/json" \
  -d '{
    "key_word": "科技",
    "sources": ["综合", "社会"],
    "page": 2
  }'
```

## 工作原理

1. **固定num=50**: 每次API请求固定获取50条数据
2. **多页查询**: 根据page参数循环调用API
3. **智能停止**: 当某页返回数量<50时，停止该数据源的后续查询
4. **多源整合**: 支持同时查询多个数据源，结果合并返回

## 项目结构

```
Python-clawer/
├── entity/
│   └── crawler_request.py          # 请求/响应实体
├── service/
│   └── tianapi_crawler_service.py  # 爬虫服务
├── controller/
│   └── crawler_controller.py       # API控制器
├── utils/
│   ├── proxy_pool.py               # 代理池（可选）
│   └── proxy_manager.py            # 代理管理器（可选）
├── config/
│   └── settings.py                 # 配置管理
├── .env.example                    # 配置示例
├── test_crawler_api.py             # 测试脚本
└── main.py                         # 主应用
```

## 代理支持（可选）

如果需要使用代理，请查看：
- `docs/PROXY_CONFIG.md` - 代理配置指南
- `docs/PROXY_POOL_GUIDE.md` - 代理池搭建
- `docs/PROXY_QUICK_START.md` - 快速开始

## API文档

启动服务后访问：`http://localhost:8088/docs`

## 常见问题

### Q1: API返回错误？

**A**: 检查：
1. TIANAPI_KEY是否正确
2. 天行数据账户余额是否充足
3. API调用次数是否超限

### Q2: 如何获取更多数据？

**A**: 增加page参数值，例如：
```json
{
  "page": 5
}
```

### Q3: 支持哪些数据源？

**A**: 目前支持：
- "综合" - 综合新闻
- "社会" - 社会新闻

可以同时查询多个数据源。

### Q4: 为什么有时候获取不到50条？

**A**:
- 当前页面数据不足50条
- 关键词匹配的结果较少
- 已经是最后一页

系统会自动停止该数据源的后续查询。

## 技术栈

- FastAPI - Web框架
- Requests - HTTP客户端
- Pydantic - 数据验证
- Uvicorn - ASGI服务器

## 许可证

MIT License
