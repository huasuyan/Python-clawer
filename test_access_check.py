"""
检测是否被新华网限制访问
"""
from selenium import webdriver
from selenium.webdriver.edge.options import Options
import time


def test_access():
    """测试是否能正常访问新华网搜索"""
    print("=" * 80)
    print("新华网访问检测")
    print("=" * 80)
    
    options = Options()
    # 不使用无头模式，方便观察
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = None
    try:
        print("\n1. 启动浏览器...")
        driver = webdriver.Edge(options=options)
        
        # 隐藏webdriver特征
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("2. 访问新华网搜索页面...")
        url = "https://so.news.cn/#search/1/%E7%A7%91%E6%8A%80/1/0"
        driver.get(url)
        
        print("3. 等待页面加载（10秒）...")
        time.sleep(10)
        
        print("4. 检查页面内容...")
        page_source = driver.page_source
        
        # 检查是否被限制
        if "403" in page_source or "forbidden" in page_source.lower():
            print("\n✗ 检测结果: 访问被拒绝 (403)")
            print("建议: 您的IP可能被限制，请更换IP或等待24小时")
            return False
        
        elif "验证" in page_source or "captcha" in page_source.lower():
            print("\n⚠ 检测结果: 需要验证码")
            print("建议: 网站要求人工验证，请手动完成验证后再试")
            return False
        
        elif len(page_source) < 1000:
            print("\n⚠ 检测结果: 页面内容异常（内容过少）")
            print(f"页面长度: {len(page_source)} 字符")
            print("建议: 可能被检测为机器人，尝试增加延迟或使用代理")
            return False
        
        elif "新华" in page_source or "搜索" in page_source:
            print("\n✓ 检测结果: 访问正常")
            print(f"页面长度: {len(page_source)} 字符")
            print("页面标题:", driver.title)
            
            # 保存页面截图
            try:
                screenshot_file = "access_test_screenshot.png"
                driver.save_screenshot(screenshot_file)
                print(f"截图已保存: {screenshot_file}")
            except:
                pass
            
            return True
        
        else:
            print("\n⚠ 检测结果: 无法确定")
            print(f"页面长度: {len(page_source)} 字符")
            print("建议: 请手动检查浏览器窗口")
            
            # 保存HTML用于分析
            with open("access_test_page.html", "w", encoding="utf-8") as f:
                f.write(page_source)
            print("页面HTML已保存: access_test_page.html")
            
            return None
    
    except Exception as e:
        print(f"\n✗ 检测失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        if driver:
            print("\n5. 关闭浏览器...")
            input("按回车键关闭浏览器...")
            driver.quit()


def main():
    print("此脚本将测试您是否能正常访问新华网搜索")
    print("浏览器窗口会打开，请观察页面是否正常显示")
    print("=" * 80)
    
    input("按回车键开始测试...")
    
    result = test_access()
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)
    
    if result is True:
        print("\n✓ 您可以正常访问新华网")
        print("\n建议:")
        print("1. 可以继续使用爬虫")
        print("2. 建议增加延迟时间，避免再次被限制")
        print("3. 每次抓取不要超过5页")
        
    elif result is False:
        print("\n✗ 您的访问受到限制")
        print("\n解决方案:")
        print("1. 等待24小时后再试")
        print("2. 更换IP地址（重启路由器/使用VPN）")
        print("3. 使用代理IP")
        print("4. 查看文档: docs/ANTI_CRAWLER.md")
        
    else:
        print("\n⚠ 无法确定访问状态")
        print("\n建议:")
        print("1. 检查保存的HTML文件: access_test_page.html")
        print("2. 查看截图: access_test_screenshot.png")
        print("3. 手动访问: https://so.news.cn")


if __name__ == "__main__":
    main()
