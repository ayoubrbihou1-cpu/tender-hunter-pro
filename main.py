import os
import time
import json
import requests
import html # مكتبة رسمية لتنظيف HTML
from google import genai 
from seleniumbase import Driver
from datetime import datetime

# --- بروتوكول الإعدادات العليا ---
CONFIG = {
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
    "TELEGRAM_TOKEN": os.getenv("TELEGRAM_TOKEN"),
    "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
    "TARGET_URL": "https://www.facebook.com/marketplace/fez/propertyrentals/?exact=false",
    "MODEL_ID": "gemini-2.5-flash",
    "WAIT_BETWEEN_DEALS": 65 
}

client = genai.Client(api_key=CONFIG["GEMINI_API_KEY"])

class UltimateHTMLHunter:
    def __init__(self):
        self.driver = None
        self.deals = []

    def log(self, msg, status="INFO"):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{status}] 🛡️ {msg}")

    def init_session(self):
        self.log("إقلاع المحرك الفولاذي (V14)...")
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
            self.log(f"فشل الجلسة: {e}", "CRITICAL")
            raise

    def hunt_listings(self):
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

    def send_to_telegram(self, report, image_url):
        """إرسال بنظام HTML المستقر 100%"""
        url = f"https://api.telegram.org/bot{CONFIG['TELEGRAM_TOKEN']}/sendPhoto"
        
        # تنظيف النص ليتوافق مع HTML تيليغرام
        safe_report = html.escape(report).replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')
        
        payload = {
            "chat_id": CONFIG["TELEGRAM_CHAT_ID"],
            "photo": image_url,
            "caption": safe_report,
            "parse_mode": "HTML"
        }
        
        try:
            res = requests.post(url, json=payload, timeout=15)
            if res.status_code == 200:
                self.log("✅ تم الإرسال الفعلي بنظام HTML.")
            else:
                self.log(f"❌ خطأ تيليغرام: {res.text}", "ERROR")
        except Exception as e:
            self.log(f"خطأ تقني: {e}", "ERROR")

    def analyze_and_broadcast(self):
        for i, deal in enumerate(self.deals):
            self.log(f"تحليل الهمزة {i+1}/{len(self.deals)}...")
            
            # برومبت يفرض وسوم HTML بسيطة
            prompt = f"""
            Analyze this property: {json.dumps(deal, ensure_ascii=False)}
            Output MUST be in Moroccan Darija. Use ONLY <b> tags for bolding.
            Example: <b>[Title]</b>
            """
            
            try:
                response = client.models.generate_content(model=CONFIG["MODEL_ID"], contents=prompt)
                report = response.text
                self.send_to_telegram(report, deal['image'])
                time.sleep(CONFIG["WAIT_BETWEEN_DEALS"])
            except Exception as e:
                self.log(f"خطأ Gemini: {e}", "ERROR")

    def run(self):
        try:
            self.init_session()
            self.hunt_listings()
            self.analyze_and_broadcast()
        finally:
            if self.driver: self.driver.quit()

if __name__ == "__main__":
    UltimateHTMLHunter().run()