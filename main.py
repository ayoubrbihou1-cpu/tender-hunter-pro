import os
import time
import random
import json
import requests
import re
from google import genai 
from seleniumbase import Driver
from datetime import datetime

# --- بروتوكول الإعدادات النخبوية ---
CONFIG = {
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
    "TELEGRAM_TOKEN": os.getenv("TELEGRAM_TOKEN"),
    "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
    "TARGET_URL": "https://www.facebook.com/marketplace/fez/propertyrentals/?exact=false",
    "MODEL_ID": "gemini-2.5-flash",
    "WAIT_BETWEEN_DEALS": 65 
}

client = genai.Client(api_key=CONFIG["GEMINI_API_KEY"])

class UltimateEliteHunter:
    def __init__(self):
        self.driver = None
        self.deals = []

    def log(self, msg, status="INFO"):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{status}] 🛡️ {msg}")

    def escape_markdown(self, text):
        """تجهيز النص لتيليغرام وتفادي الرموز القاتلة"""
        escape_chars = r'_*[]()~`>#+-=|{}.!'
        return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)

    def init_session(self):
        """اختراق الجلسة بوضعية الشبح"""
        self.log("إقلاع المحرك الفولاذي...")
        self.driver = Driver(uc=True, headless=True)
        try:
            self.driver.get("https://web.facebook.com")
            with open("cookies.json", "r") as f:
                cookies = json.load(f)
                for c in cookies:
                    if 'sameSite' in c and c['sameSite'] not in ["Strict", "Lax", "None"]:
                        del c['sameSite']
                    try: self.driver.add_cookie(c)
                    except: continue
            self.driver.refresh()
            time.sleep(5)
            self.log("تم تأكيد الهوية الرقمية.")
        except Exception as e:
            self.log(f"فشل في زرع الكوكيز: {e}", "CRITICAL")
            raise

    def hunt_listings(self):
        """قنص الهمزات من ماركت بلايس فاس"""
        self.log(f"التوجه للهدف: {CONFIG['TARGET_URL']}")
        self.driver.get(CONFIG["TARGET_URL"])
        time.sleep(15)
        self.driver.execute_script("window.scrollTo(0, 800);")
        time.sleep(5)
        cards = self.driver.find_elements("css selector", 'div[style*="max-width"]')[:3]
        for card in cards:
            try:
                img = card.find_element("css selector", "img").get_attribute("src")
                raw_text = card.text.split('\n')
                link = card.find_element("css selector", "a").get_attribute("href").split('?')[0]
                if "/marketplace/item/" in link and len(raw_text) >= 2:
                    self.deals.append({"price": raw_text[0], "title": raw_text[1], "link": link, "image": img})
            except: continue
        self.log(f"تم قنص {len(self.deals)} بطاقات.")

    def send_safe_telegram(self, report, photo_url):
        """إرسال ذكي مع حل مشكلة الـ f-string"""
        url = f"https://api.telegram.org/bot{CONFIG['TELEGRAM_TOKEN']}/sendPhoto"
        
        # 1. الميساج المنسق بـ MarkdownV2
        payload = {
            "chat_id": CONFIG["TELEGRAM_CHAT_ID"],
            "photo": photo_url,
            "caption": report,
            "parse_mode": "MarkdownV2"
        }
        
        try:
            res = requests.post(url, json=payload, timeout=15)
            if res.status_code == 200:
                self.log("✅ تم الإرسال الفعلي لتيليغرام.")
            else:
                self.log(f"❌ تنسيق مرفوض (Code {res.status_code}). كنصيفط نص عادي...", "WARNING")
                # تصحيح الخطأ: معالجة النص خارج الـ f-string لتفادي SyntaxError
                clean_text = report.replace('\\', '')
                fallback_caption = f"⚠️ همزة جديدة (تنسيق مبسط):\n{clean_text}"
                
                requests.post(url, json={
                    "chat_id": CONFIG["TELEGRAM_CHAT_ID"],
                    "photo": photo_url,
                    "caption": fallback_caption
                })
        except Exception as e:
            self.log(f"خطأ تقني ف تيليغرام: {e}", "ERROR")

    def analyze_and_broadcast(self):
        """التحليل النخبوي بـ Gemini 2.5 Flash"""
        for i, deal in enumerate(self.deals):
            self.log(f"تحليل الهمزة {i+1}/{len(self.deals)}...")
            prompt = f"Analyze this Fez property: {json.dumps(deal, ensure_ascii=False)}. Convert price to Million and write a Professional Business Darija report."
            try:
                response = client.models.generate_content(model=CONFIG["MODEL_ID"], contents=prompt)
                raw_report = response.text
                safe_report = self.escape_markdown(raw_report)
                self.send_safe_telegram(safe_report, deal['image'])
                time.sleep(CONFIG["WAIT_BETWEEN_DEALS"])
            except Exception as e:
                self.log(f"خطأ في التحليل: {e}", "ERROR")

    def run(self):
        try:
            self.init_session()
            self.hunt_listings()
            self.analyze_and_broadcast()
        finally:
            if self.driver: self.driver.quit()

if __name__ == "__main__":
    UltimateEliteHunter().run()