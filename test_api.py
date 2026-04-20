"""
新华网搜索API测试脚本
"""
import requests
import json
import time


BASE_URL = "http://localhost:8088"


def test_api_connection():
    """测试API连接"""
    print("=" * 80)
    print("测试1: API连接测试")
    print("=" * 80)
    
    try:
        response = requests.get(f"{BASE_URL}/api/xinhua/test", timeout=10)
        result = response.json()
        print(f"✓ 连接成功: {result}")
        return True
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        return False


def test_search_news_title(keyword="科技", pages=2):
    """测试新闻标题搜索"""
    print("\n" + "=" * 80)
    print(f"测试2: 新闻标题搜索 - 关键词'{keyword}'，抓取{pages+1}页")
    print("=" * 80)
    
    data = {
        "keyword": keyword,
        "search_type": 1,  # 新闻
        "search_fields": 1,  # 标题
        "sort_field": 0,  # 按时间排序
        "start_page": 0,
        "end_page": pages,
        "browser_type": "edge"
    }
    
    print(f"请求参数: {json.dumps(data, ensure_ascii=False, indent=2)}")
    print("\n开始请求...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/xinhua/search",
            json=data,
            timeout=300  # 5分钟超时
        )
        
        result = response.json()
        
        if result.get("code") == 200:
            print(f"\n✓ 搜索成功!")
            print(f"消息: {result.get('msg')}")
            
            results = result.get("data", [])
            print(f"\n共获取 {len(results)} 条结果")
            
            # 显示前5条
            print("\n前5条结果:")
            for i, item in enumerate(results[:5], 1):
                print(f"\n{i}. {item['title']}")
                print(f"   链接: {item['url']}")
                print(f"   页码: 第{item['page'] + 1}页")
            
            # 保存结果
            output_file = f"test_results_{keyword}_news.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n结果已保存到: {output_file}")
            
            return True
        else:
            print(f"\n✗ 搜索失败: {result}")
            return False
            
    except Exception as e:
        print(f"\n✗ 请求失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_search_academic(keyword="人工智能", pages=1):
    """测试学术文献搜索"""
    print("\n" + "=" * 80)
    print(f"测试3: 学术文献搜索 - 关键词'{keyword}'，抓取{pages+1}页")
    print("=" * 80)
    
    data = {
        "keyword": keyword,
        "search_type": 2,  # 学术文献
        "start_page": 0,
        "end_page": pages,
        "browser_type": "edge"
    }
    
    print(f"请求参数: {json.dumps(data, ensure_ascii=False, indent=2)}")
    print("\n开始请求...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/xinhua/search",
            json=data,
            timeout=300
        )
        
        result = response.json()
        
        if result.get("code") == 200:
            print(f"\n✓ 搜索成功!")
            print(f"消息: {result.get('msg')}")
            
            results = result.get("data", [])
            print(f"\n共获取 {len(results)} 条结果")
            
            # 显示前3条
            print("\n前3条结果:")
            for i, item in enumerate(results[:3], 1):
                print(f"\n{i}. {item['title']}")
                print(f"   链接: {item['url']}")
                print(f"   页码: 第{item['page'] + 1}页")
            
            # 保存结果
            output_file = f"test_results_{keyword}_academic.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n结果已保存到: {output_file}")
            
            return True
        else:
            print(f"\n✗ 搜索失败: {result}")
            return False
            
    except Exception as e:
        print(f"\n✗ 请求失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_search_with_edge():
    """测试使用Edge浏览器"""
    print("\n" + "=" * 80)
    print("测试4: 使用Edge浏览器搜索")
    print("=" * 80)
    
    data = {
        "keyword": "经济",
        "search_type": 1,
        "search_fields": 1,
        "sort_field": 0,
        "start_page": 0,
        "end_page": 0,  # 只抓取1页
        "browser_type": "edge"
    }
    
    print(f"请求参数: {json.dumps(data, ensure_ascii=False, indent=2)}")
    print("\n开始请求...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/xinhua/search",
            json=data,
            timeout=300
        )
        
        result = response.json()
        
        if result.get("code") == 200:
            print(f"\n✓ 搜索成功!")
            results = result.get("data", [])
            print(f"共获取 {len(results)} 条结果")
            return True
        else:
            print(f"\n✗ 搜索失败: {result}")
            return False
            
    except Exception as e:
        print(f"\n✗ 请求失败: {e}")
        return False


def main():
    """主测试函数"""
    print("新华网搜索API测试")
    print("=" * 80)
    print("注意: 请确保服务已启动 (python main.py)")
    print("=" * 80)
    
    # 等待用户确认
    input("\n按回车键开始测试...")
    
    results = []
    
    # 测试1: API连接
    results.append(("API连接测试", test_api_connection()))
    time.sleep(2)
    
    # 测试2: 新闻标题搜索
    results.append(("新闻标题搜索", test_search_news_title("科技", pages=2)))
    time.sleep(2)
    
    # 测试3: 学术文献搜索
    results.append(("学术文献搜索", test_search_academic("人工智能", pages=1)))
    time.sleep(2)
    
    # 测试4: Edge浏览器（可选，如果没有Edge可以跳过）
    print("\n是否测试Edge浏览器？(y/n，默认n): ", end="")
    choice = input().strip().lower()
    if choice == 'y':
        results.append(("Edge浏览器测试", test_search_with_edge()))
    
    # 汇总结果
    print("\n\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    
    for test_name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    
    print("\n" + "=" * 80)
    print(f"总计: {passed}/{total} 个测试通过")
    print("=" * 80)


if __name__ == "__main__":
    main()
