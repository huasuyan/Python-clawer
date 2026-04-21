"""
爬虫接口测试脚本
"""
import requests
import json
import time
from datetime import datetime


BASE_URL = "http://localhost:8088"


def print_header(title):
    """打印标题"""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def print_section(title):
    """打印小节标题"""
    print("\n" + "-" * 80)
    print(title)
    print("-" * 80)


def save_result(data, filename):
    """保存结果到文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✓ 结果已保存到: {filename}")
    except Exception as e:
        print(f"✗ 保存失败: {e}")


def test_connection():
    """测试服务连接"""
    print_header("测试1: 服务连接测试")

    try:
        response = requests.get(f"{BASE_URL}/api/python/crawler/test", timeout=10)
        result = response.json()

        if result.get("code") == 1:
            print("✓ 服务连接正常")
            print(f"  支持的数据源: {result.get('data', {}).get('supported_sources')}")
            print(f"  每页最大数量: {result.get('data', {}).get('max_num_per_page')}")
            return True
        else:
            print(f"✗ 服务异常: {result.get('msg')}")
            return False

    except Exception as e:
        print(f"✗ 连接失败: {e}")
        print("\n请确保:")
        print("  1. 服务已启动 (python main.py)")
        print("  2. 端口8088未被占用")
        print("  3. 已配置TIANAPI_KEY")
        return False


def test_single_source(keyword, source, page=1):
    """测试单个数据源"""
    print_section(f"测试: {source}新闻 - 关键词'{keyword}'")

    data = {
        "key_word": keyword,
        "sources": [source],
        "page": page
    }

    print(f"请求参数: {json.dumps(data, ensure_ascii=False)}")

    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/python/crawler/runIntegration",
            json=data,
            timeout=120
        )
        elapsed_time = time.time() - start_time

        result = response.json()

        if result.get("code") == 1:
            data_list = result.get("data", {}).get("dataList", [])
            print(f"✓ 成功！获取 {len(data_list)} 条数据 (耗时: {elapsed_time:.2f}秒)")

            if data_list:
                # 显示统计信息
                print(f"\n数据统计:")
                print(f"  总条数: {len(data_list)}")
                print(f"  有图片: {sum(1 for item in data_list if item.get('picUrl'))}")
                print(f"  有内容: {sum(1 for item in data_list if item.get('content'))}")

                # 显示前3条
                print(f"\n前3条数据:")
                for i, item in enumerate(data_list[:3], 1):
                    print(f"\n  [{i}] {item.get('title')}")
                    print(f"      来源: {item.get('source')}")
                    print(f"      时间: {item.get('publishTime')}")
                    print(f"      链接: {item.get('url')}")
                    if item.get('picUrl'):
                        print(f"      图片: {item.get('picUrl')[:60]}...")

                return True, data_list
            else:
                print("⚠ 未获取到数据")
                return False, []
        else:
            print(f"✗ 失败: {result.get('msg')}")
            return False, []

    except Exception as e:
        print(f"✗ 请求失败: {e}")
        import traceback
        traceback.print_exc()
        return False, []


def test_multiple_sources(keyword, sources, page=2):
    """测试多个数据源"""
    print_section(f"测试: 多数据源 - 关键词'{keyword}', 页数{page}")

    data = {
        "key_word": keyword,
        "sources": sources,
        "page": page
    }

    print(f"请求参数: {json.dumps(data, ensure_ascii=False)}")

    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/python/crawler/runIntegration",
            json=data,
            timeout=180
        )
        elapsed_time = time.time() - start_time

        result = response.json()

        if result.get("code") == 1:
            data_list = result.get("data", {}).get("dataList", [])
            print(f"✓ 成功！获取 {len(data_list)} 条数据 (耗时: {elapsed_time:.2f}秒)")

            if data_list:
                # 按数据源统计
                source_stats = {}
                for item in data_list:
                    source = item.get('source', '未知')
                    source_stats[source] = source_stats.get(source, 0) + 1

                print(f"\n数据源统计:")
                for source, count in source_stats.items():
                    print(f"  {source}: {count}条")

                # 显示每个数据源的第一条
                print(f"\n各数据源示例:")
                shown_sources = set()
                for item in data_list:
                    source = item.get('source', '未知')
                    if source not in shown_sources:
                        print(f"\n  [{source}] {item.get('title')}")
                        print(f"      时间: {item.get('publishTime')}")
                        shown_sources.add(source)

                return True, data_list
            else:
                print("⚠ 未获取到数据")
                return False, []
        else:
            print(f"✗ 失败: {result.get('msg')}")
            return False, []

    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False, []


def test_pagination():
    """测试分页功能"""
    print_section("测试: 分页功能")

    keyword = "科技"
    source = "综合"

    print(f"测试关键词'{keyword}'的分页数据...")

    all_results = []
    for page in range(1, 4):  # 测试3页
        print(f"\n  第{page}页:")
        data = {
            "key_word": keyword,
            "sources": [source],
            "page": page
        }

        try:
            response = requests.post(
                f"{BASE_URL}/api/python/crawler/runIntegration",
                json=data,
                timeout=60
            )
            result = response.json()

            if result.get("code") == 1:
                data_list = result.get("data", {}).get("dataList", [])
                print(f"    获取 {len(data_list)} 条数据")
                all_results.extend(data_list)
            else:
                print(f"    失败: {result.get('msg')}")
                break
        except Exception as e:
            print(f"    错误: {e}")
            break

        time.sleep(1)  # 避免请求过快

    print(f"\n分页测试完成，共获取 {len(all_results)} 条数据")
    return len(all_results) > 0


def run_all_tests():
    """运行所有测试"""
    print_header("爬虫接口完整测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = []
    all_data = []

    # 测试1: 连接测试
    if not test_connection():
        print("\n✗ 服务连接失败，终止测试")
        return

    results.append(("服务连接", True))
    time.sleep(1)

    # 测试2: 综合新闻
    print_header("测试2: 综合新闻")
    success, data = test_single_source("科技", "综合", page=1)
    results.append(("综合新闻", success))
    if data:
        all_data.extend(data)
    time.sleep(2)

    # 测试3: 社会新闻
    print_header("测试3: 社会新闻")
    success, data = test_single_source("教育", "社会", page=1)
    results.append(("社会新闻", success))
    if data:
        all_data.extend(data)
    time.sleep(2)

    # 测试4: 多数据源
    print_header("测试4: 多数据源整合")
    success, data = test_multiple_sources("经济", ["综合", "社会"], page=2)
    results.append(("多数据源", success))
    if data:
        save_result(data, f"test_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    time.sleep(2)

    # 测试5: 分页
    print_header("测试5: 分页功能")
    success = test_pagination()
    results.append(("分页功能", success))

    # 汇总结果
    print_header("测试结果汇总")

    for test_name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"  {test_name}: {status}")

    total = len(results)
    passed = sum(1 for _, success in results if success)

    print(f"\n总计: {passed}/{total} 个测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠ {total - passed} 个测试失败")


def interactive_test():
    """交互式测试"""
    print_header("交互式测试模式")

    keyword = input("请输入关键词 (默认: 科技): ").strip() or "科技"

    print("\n选择数据源:")
    print("  1. 综合")
    print("  2. 社会")
    print("  3. 综合+社会")
    choice = input("请选择 (1/2/3, 默认: 3): ").strip() or "3"

    if choice == "1":
        sources = ["综合"]
    elif choice == "2":
        sources = ["社会"]
    else:
        sources = ["综合", "社会"]

    page = input("请输入页数 (默认: 1): ").strip() or "1"
    page = int(page)

    print_section("开始测试")
    success, data = test_multiple_sources(keyword, sources, page)

    if success and data:
        save_choice = input("\n是否保存结果? (y/n): ").strip().lower()
        if save_choice == 'y':
            filename = f"test_result_{keyword}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            save_result(data, filename)


def main():
    print("=" * 80)
    print("爬虫接口测试工具")
    print("=" * 80)
    print("\n选择测试模式:")
    print("  1. 完整测试 (推荐)")
    print("  2. 交互式测试")
    print("  3. 快速测试 (仅测试连接)")

    choice = input("\n请选择 (1/2/3, 默认: 1): ").strip() or "1"

    if choice == "1":
        run_all_tests()
    elif choice == "2":
        if test_connection():
            interactive_test()
    elif choice == "3":
        test_connection()
    else:
        print("无效选择")

    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()
