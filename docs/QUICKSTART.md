# 新华网搜索爬虫 - 快速启动指南

## 项目结构

```
Python-clawer/
├── entity/
│   └── xinhua_search_request.py    # 请求和响应实体类
├── service/
│   └── xinhua_search_service.py    # 爬虫服务核心逻辑
├── controller/
│   └── xinhua_controller.py        # API控制器
├── docs/
│   └── XINHUA_API.md              # API详细文档
├── test_xinhua_service.py         # 服务测试脚本
├── test_fetch_html.py             # Windows测试脚本（Edge）
├── test_fetch_html_linux.py       # Linux测试脚本（Chrome）
└── main.py                        # 主应用入口
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python main.py
```

服务将在 `http://localhost:8088` 启动

### 3. 访问API文档

浏览器打开: `http://localhost:8088/docs`

### 4. 测试接口

#### 方法1: 使用测试脚本

```bash
python test_xinhua_service.py
```

#### 方法2: 使用curl

```bash
curl -X POST "http://localhost:8088/api/xinhua/search" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "科技",
    "search_type": 1,
    "search_fields": 1,
    "sort_field": 0,
    "start_page": 0,
    "end_page": 2,
    "browser_type": "chrome"
  }'
```

#### 方法3: 使用Python

```python
import requests

response = requests.post(
    "http://localhost:8088/api/xinhua/search",
    json={
        "keyword": "科技",
        "search_type": 1,
        "search_fields": 1,
        "sort_field": 0,
        "start_page": 0,
        "end_page": 2,
        "browser_type": "chrome"
    }
)

print(response.json())
```

## 参数配置

### 必填参数

- `keyword`: 搜索关键词

### 可选参数

- `search_type`: 1=新闻（默认），2=学术文献
- `search_fields`: 0=正文，1=标题（仅新闻搜索时有效）
- `sort_field`: 0=时间，1=相关度（仅新闻搜索时有效）
- `start_page`: 起始页码，从0开始（默认0）
- `end_page`: 结束页码（默认0）
- `browser_type`: chrome（默认）或 edge

## 常见使用场景

### 场景1: 搜索最新科技新闻

```json
{
  "keyword": "科技",
  "search_type": 1,
  "search_fields": 1,
  "sort_field": 0,
  "start_page": 0,
  "end_page": 4,
  "browser_type": "chrome"
}
```

### 场景2: 搜索人工智能相关内容（按相关度）

```json
{
  "keyword": "人工智能",
  "search_type": 1,
  "search_fields": 0,
  "sort_field": 1,
  "start_page": 0,
  "end_page": 2,
  "browser_type": "chrome"
}
```

### 场景3: 搜索学术文献

```json
{
  "keyword": "量子计算",
  "search_type": 2,
  "start_page": 0,
  "end_page": 1,
  "browser_type": "chrome"
}
```

## 注意事项

1. **浏览器选择**:
   - Windows推荐使用Edge
   - Linux必须使用Chrome

2. **性能优化**:
   - 每页抓取间隔3秒
   - 页面加载等待5秒
   - 建议单次不超过10页

3. **错误处理**:
   - 如果某页失败会自动跳过
   - 最终返回成功抓取的所有结果

## 故障排查

### 问题1: 浏览器驱动找不到

**解决方案**: 确保已安装对应浏览器，Selenium会自动下载驱动

### 问题2: Linux上Chrome启动失败

**解决方案**: 安装Chrome浏览器
```bash
sudo apt install -y google-chrome-stable
```

### 问题3: 页面加载超时

**解决方案**: 增加等待时间，修改 `xinhua_search_service.py` 中的 `wait_time`

## 更多信息

详细API文档请查看: [docs/XINHUA_API.md](docs/XINHUA_API.md)
