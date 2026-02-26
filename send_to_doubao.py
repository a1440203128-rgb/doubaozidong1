import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import os

# ===== 需要你修改的部分 =====
# 企业微信机器人的 Webhook 地址（稍后会设置成密钥，这里先留空）
WEBHOOK_URL = os.environ.get("WECHAT_WEBHOOK", "")
# 你想发送的内容
MESSAGE = 「报猫眼专业版实时累计想看：
千金不换、澎湖海战、洛杉矶劫案、奇迹梦之队、呼啸山庄,天才游戏」
只要每个电影名字加数据不要其他文字，标题加日期"
# ===========================

def send_to_wechat(content):
    """发送消息到企业微信"""
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
    driver = None
    try:
        # 配置无头浏览器（GitHub Actions 环境可用）
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1280,720')
        
        # 启动浏览器
        driver = webdriver.Chrome(options=chrome_options)
        print("浏览器启动成功")
        
        # 打开豆包
        driver.get('https://www.doubao.com/chat/')
        time.sleep(5)  # 等待页面加载
        
        # 找到输入框（通常是用 textarea）
        input_box = driver.find_element(By.TAG_NAME, 'textarea')
        input_box.send_keys(MESSAGE)
        time.sleep(1)
        input_box.send_keys(Keys.RETURN)
        print("消息已发送")
        
        # 等待回复
        time.sleep(5)
        
        # 尝试获取豆包的回复
        reply_text = "未获取到回复"
        try:
            # 尝试几种常见的选择器
            selectors = [
                '[class*="message"]:last-child',
                '[class*="chat"]:last-child',
                '.assistant-message',
                '.ai-message'
            ]
            for selector in selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    reply_text = elements[-1].text
                    if reply_text:
                        break
        except:
            pass
        
        print(f"获取到回复：{reply_text[:100]}...")
        
        # 推送到企业微信
        result_msg = f"""✅ 豆包每日任务执行成功

⏰ 时间：{time.strftime('%Y-%m-%d %H:%M:%S')}
📝 发送内容：{MESSAGE}
💬 豆包回复：{reply_text}"""
        send_to_wechat(result_msg)
        
    except Exception as e:
        error_msg = f"""❌ 豆包每日任务执行失败

⏰ 时间：{time.strftime('%Y-%m-%d %H:%M:%S')}
❌ 错误信息：{str(e)}"""
        send_to_wechat(error_msg)
        print(f"错误：{e}")
    
    finally:
        if driver:
            driver.quit()
            print("浏览器已关闭")

if __name__ == "__main__":
    main()
