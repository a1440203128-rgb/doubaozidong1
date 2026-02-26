import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1280,720')
        
        driver = webdriver.Chrome(options=chrome_options)
        print("浏览器启动成功")
        
        driver.get('https://www.doubao.com/chat/')
        print("等待页面加载...")
        
        # 使用显式等待，最多等15秒，直到输入框可以被点击
        wait = WebDriverWait(driver, 15)
        
        # 尝试多种定位方式来找到输入框
        input_selectors = [
            (By.CSS_SELECTOR, '#root > div > div.chat-input > textarea'),#chat-route-layout > div > main > div > div.-mt-\[var\(--header-height\)\].flex.w-full.flex-grow.flex-col.items-center.px-16 > div.relative.flex.flex-col.w-full.min-h-\[var\(--input-guidance-input-container-min-height\)\].max-h-\[var\(--input-guidance-input-container-max-height\]\).max-w-\[var\(--content-max-width\)\] > div > div.flex.flex-col-reverse > div > div.relative.flex.flex-col.max-h-\(--input-guidance-input-container-max-height\,unset\).rounded-\[inherit\].border-\(--input-guidance-input-container-border\).bg-\(--input-guidance-input-container-background\) > div.relative.flex.flex-col-reverse.justify-between.items-end.gap-14.relative.w-full.flex-1.min-h-0.p-10 > div.w-full.flex.min-h-\(--input-guidance-input-editor-wrapper-min-height\,0\).px-10.pt-6 > div > div.container-kxxSU4.flex-1.w-0.min-w-0.\!border-none.\!bg-transparent.max-h-\[calc\(var\(--input-guidance-input-container-max-height\)-var\(--custom-area-height\,0px\)-36px-16px-14px-10px\)\].textarea-BnKyIt.custom-scrollbar-stmEIo.semi-input-textarea-wrapper > textarea
            (By.TAG_NAME, 'textarea'),
            (By.CSS_SELECTOR, '[contenteditable="true"]'),
            (By.CSS_SELECTOR, '.input-area [role="textbox"]'),
            (By.CSS_SELECTOR, 'div[class*="input"] div[class*="editor"]')
        ]
        
        input_box = None
        for by, selector in input_selectors:
            try:
                print(f"尝试选择器: {by}={selector}")
                input_box = wait.until(EC.element_to_be_clickable((by, selector)))
                print(f"找到输入框，使用选择器: {by}={selector}")
                break
            except:
                continue
        
        if not input_box:
            raise Exception("所有选择器都无法定位输入框")
        
        # 输入内容并发送
        input_box.click()  # 先点击一下确保激活
        input_box.send_keys("报猫眼专业版实时累计想看：")
        print("消息已输入")
        time.sleep(1)
        input_box.send_keys(Keys.RETURN)
        print("消息已发送")
        
        # 等待回复
        time.sleep(5)
        
        reply_text = "未获取到回复"
        try:
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
        
        result_msg = f"""✅ 豆包每日任务执行成功

⏰ 时间：{time.strftime('%Y-%m-%d %H:%M:%S')}
📝 发送内容：报猫眼专业版实时累计想看：
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
