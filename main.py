import os
import time
import json
import requests
import re # لإضافة نظام تنظيف الرموز
from google import genai 
from seleniumbase import Driver
from datetime import datetime

# --- بروتوكول الإعدادات العليا ---
CONFIG = {
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
    "TELEGRAM_TOKEN": os.getenv("TELEGRAM_TOKEN"),
    "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
    "TARGET_URL": "https://www.facebook.com/marketplace/fez/propertyrentals/?exact=false",
    "MODEL_ID": "gemini-2.5-flash", # الموديل المعتمد
    "WAIT_BETWEEN_DEALS": 65 # حماية الكوطا
}

client = genai.Client(api_key=CONFIG["GEMINI_API_KEY"])

class UltimateGeminiHunter:
    def __init__(self):
        self.driver = None
        self.deals = []

    def log(self, msg, status="INFO"):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{status}] 🛡️ {msg}")

    def escape_markdown(self, text):
        """تنظيف النص من الرموز اللي كتشل حركة تيليغرام"""
        # الهروب من الرموز الخاصة فـ MarkdownV2 لضمان القبول
        escape_chars = r'_*[]()~`>#+-=|{}.!'
        return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)

    def init_session(self):
        """إقلاع المحرك واختراق الجلسة"""
        self.log("إقلاع المحرك UC Mode...")
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
            self.log(f"فشل فـ الجلسة: {e}", "ERROR")

    def hunt_listings(self):
        """قنص الهمزات من فاس"""
        self.log(f"التوجه للهدف: {CONFIG['TARGET_URL']}")
        self.driver.get(CONFIG["TARGET_URL"])
        time.sleep(15)
        self.driver.execute_script("window.scrollTo(0, 800);")
        time.sleep(5)
        
        cards = self.driver.find_elements("css selector", 'div[style*="max-width"]')[:3]
        self.log(f"تم رصد {len(cards)} إعلانات أولية.")

        for card in cards:
            try:
                img = card.find_element("css selector", "img").get_attribute("src")
                raw_text = card.text.split('\n')
                link = card.find_element("css selector", "a").get_attribute("href").split('?')[0]
                if "/marketplace/item/" in link and len(raw_text) >= 2:
                    self.deals.append({
                        "price": raw_text[0],
                        "title": raw_text[1],
                        "link": link,
                        "image": img
                    })
            except: continue

    def send_to_telegram(self, report, image_url):
        """إرسال ذكي مع فحص استجابة تيليغرام"""
        url = f"https://api.telegram.org/bot{CONFIG['TELEGRAM_TOKEN']}/sendPhoto"
        
        # غانستعملو MarkdownV2 حيت هي الأكثر استقراراً مع التنظيف
        payload = {
            "chat_id": CONFIG["TELEGRAM_CHAT_ID"],
            "photo": image_url,
            "caption": report,
            "parse_mode": "MarkdownV2"
        }
        
        try:
            res = requests.post(url, json=payload, timeout=15)
            if res.status_code == 200:
                self.log("✅ تم الإرسال الفعلي لتيليغرام.")
            else:
                # لو فشل بسبب الرموز، غانصيفطوه نص عادي بلا تنسيق كخيار أمان
                self.log(f"❌ تيليغرام رفض التنسيق (Code {res.status_code}). كنحاول نصيفط نص عادي...", "WARNING")
                fallback_payload = {
                    "chat_id": CONFIG["TELEGRAM_CHAT_ID"],
                    "photo": image_url,
                    "caption": f"⚠️ همزة جديدة (تنسيق مبسط):\n{report.replace('\\', '')}",
                }
                requests.post(url, json=fallback_payload, timeout=15)
        except Exception as e:
            self.log(f"خطأ تقني فـ تيليغرام: {e}", "ERROR")

    def analyze_and_broadcast(self):
        """التحليل بذكاء Gemini وتنظيف الداتا"""
        for i, deal in enumerate(self.deals):
            self.log(f"بدء تحليل الهمزة {i+1}/{len(self.deals)}...")
            
            prompt = f"""
            Analyze this property: {json.dumps(deal, ensure_ascii=False)}
            Write a Professional Business Darija report. 
            Rules:
            1. Price to Million.
            2. Identify if it's a good deal.
            3. Use clear bullet points.
            """
            
            try:
                # الاستدعاء من Gemini 2.5 Flash
                response = client.models.generate_content(
                    model=CONFIG["MODEL_ID"],
                    contents=prompt
                )
                raw_report = response.text
                
                # تنظيف النص ليتوافق مع تيليغرام
                safe_report = self.escape_markdown(raw_report)
                
                # الإرسال مع فحص الوصول
                self.send_to_telegram(safe_report, deal['image'])
                
                self.log(f"انتظار {CONFIG['WAIT_BETWEEN_DEALS']} ثانية...")
                time.sleep(CONFIG["WAIT_BETWEEN_DEALS"])

            except Exception as e:
                self.log(f"خطأ فـ Gemini: {e}", "ERROR")

    def run(self):
        try:
            self.init_session()
            self.hunt_listings()
            self.analyze_and_broadcast()
        finally:
            if self.driver: self.driver.quit()
            self.log("نهاية المهمة بنجاح.")

if __name__ == "__main__":
    UltimateGeminiHunter().run()