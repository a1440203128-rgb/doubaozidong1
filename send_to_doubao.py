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
        # 启动浏览器（无头模式）
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        page = browser.new_page()
        print("浏览器启动成功")
        
        # 打开豆包
        page.goto('https://www.doubao.com/chat/')
        print("等待页面加载...")
        
        # 等待输入框出现（最多30秒）
        # 尝试多种定位方式，Playwright 会自动等待
        try:
            # 优先使用 placeholder 定位
            input_box = page.wait_for_selector('textarea[placeholder="给豆包发送消息"]', timeout=30000)
        except:
            try:
                # 如果没有 placeholder，尝试通用选择器
                input_box = page.wait_for_selector('textarea, [contenteditable="true"], [role="textbox"]', timeout=30000)
            except:
                # 如果还找不到，打印页面源码帮助调试
                print("页面源码片段：", page.content()[:2000])
                raise Exception("无法定位输入框")
        
        # 点击输入框并输入内容
        input_box.click()
        input_box.fill("报猫眼专业版实时累计想看：")
        print("消息已输入")
        time.sleep(1)
        input_box.press("Enter")
        print("消息已发送")
        
        # 等待回复出现
        page.wait_for_timeout(5000)
        
        # 获取最后一条消息（可能是 AI 回复）
        messages = page.query_selector_all('.message, [class*="message"]')
        reply_text = "未获取到回复"
        if messages:
            last_msg = messages[-1]
            reply_text = last_msg.text_content() or "回复内容为空"
        
        print(f"获取到回复：{reply_text[:100]}...")
        
        result_msg = f"""✅ 豆包每日任务执行成功

⏰ 时间：{time.strftime('%Y-%m-%d %H:%M:%S')}
📝 发送内容：报猫眼专业版实时累计想看：
💬 豆包回复：{reply_text}"""
        send_to_wechat(result_msg)
        
        browser.close()
        print("浏览器已关闭")

if __name__ == "__main__":
    main()
