import time
import requests
from playwright.sync_api import sync_playwright
import os

WEBHOOK_URL = os.environ.get("WECHAT_WEBHOOK", "")

def send_to_wechat(content):
    if not WEBHOOK_URL:
        print("错误：未设置企业微信 Webhook 地址")
        return
    try:
        data = {
            "msgtype": "text",
            "text": {"content": content}
        }
        resp = requests.post(WEBHOOK_URL, json=data, timeout=10)
        print(f"企业微信推送结果：{resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"企业微信推送失败：{e}")

def main():
    print("任务开始执行...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        page = browser.new_page()
        print("浏览器启动成功")
        
        # 打开豆包
        page.goto('https://www.doubao.com/chat/')
        print("等待页面加载...")
        page.wait_for_timeout(5000)  # 等待5秒，让页面充分加载
        
        # 打印当前页面标题和URL
        print("当前页面标题：", page.title())
        print("当前页面URL：", page.url)
        
        # 查找所有可能的输入框候选元素
        candidates = page.query_selector_all('textarea, [contenteditable], [role="textbox"], input, div[class*="input"], div[class*="editor"]')
        print(f"找到 {len(candidates)} 个候选元素：")
        
        for i, el in enumerate(candidates):
            # 获取元素标签名
            tag = el.evaluate('el => el.tagName')
            # 获取常用属性
            attrs = el.evaluate('''el => ({
                id: el.id,
                class: el.className,
                placeholder: el.placeholder,
                contenteditable: el.contentEditable,
                role: el.getAttribute('role'),
                type: el.getAttribute('type'),
                'aria-label': el.getAttribute('aria-label'),
                outerHTML: el.outerHTML.substring(0, 200)  // 截取前200字符避免日志过长
            })''')
            print(f"\n--- 候选元素 {i} ---")
            print(f"标签: {tag}")
            for key, value in attrs.items():
                print(f"{key}: {value}")
        
        # 尝试截取整个页面源码（前5000字符）以便分析
        html_snippet = page.content()[:5000]
        print("\n页面源码片段（前5000字符）：")
        print(html_snippet)
        
        # 最后抛出异常，因为我们还在调试阶段
        raise Exception("调试信息已打印，请根据日志分析正确的定位器")
        
        browser.close()

if __name__ == "__main__":
    main()
