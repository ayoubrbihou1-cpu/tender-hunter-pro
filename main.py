import os
import time
import json
import requests
from google import genai  # المكتبة الجديدة لـ 2026
from seleniumbase import Driver
from datetime import datetime

# --- إعدادات مركز القيادة العليا ---
CONFIG = {
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
    "TELEGRAM_TOKEN": os.getenv("TELEGRAM_TOKEN"),
    "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
    "TARGET_URL": "https://www.facebook.com/marketplace/fez/propertyrentals/?exact=false",
    "MODEL_ID": "gemini-3-pro-preview" # الموديل القناص
}

# إقلاع محرك Gemini 3
client = genai.Client(api_key=CONFIG["GEMINI_API_KEY"])

class EliteGemini3Hunter:
    def __init__(self):
        self.driver = None
        self.deals = []

    def log(self, msg, status="INFO"):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{status}] 🛡️ {msg}")

    def init_session(self):
        """اختراق الجلسة بوضعية الشبح"""
        self.log("إقلاع المحرك UC Mode...")
        self.driver = Driver(uc=True, headless=True)
        try:
            self.driver.get("https://web.facebook.com")
            with open("cookies.json", "r") as f:
                cookies = json.load(f)
                for c in cookies:
                    # حل مشكلة AssertionError
                    if 'sameSite' in c and c['sameSite'] not in ["Strict", "Lax", "None"]:
                        del c['sameSite']
                    try: self.driver.add_cookie(c)
                    except: continue
            self.driver.refresh()
            time.sleep(5)
            self.log("تم تأكيد الهوية الرقمية بنجاح.")
        except Exception as e:
            self.log(f"فشل فـ الجلسة: {e}", "ERROR")

    def hunt_listings(self):
        """قنص الهمزات من ماركت بلايس فاس"""
        self.log(f"التوجه للهدف: {CONFIG['TARGET_URL']}")
        self.driver.get(CONFIG["TARGET_URL"])
        time.sleep(15)
        self.driver.execute_script("window.scrollTo(0, 800);")
        time.sleep(5)
        
        cards = self.driver.find_elements("css selector", 'div[style*="max-width"]')[:5]
        self.log(f"تم رصد {len(cards)} إعلان. جاري الاستخراج المعزول...")

        # فصل البيانات لتفادي stale element reference
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

    def analyze_and_broadcast(self):
        """التحليل بذكاء Gemini 3"""
        for deal in self.deals:
            self.log(f"Gemini 3 كايحلل: {deal['title'][:20]}...")
            prompt = f"Analyze this property: {json.dumps(deal, ensure_ascii=False)}. Write a high-level Business Darija report with Million conversion and Pros/Cons."
            try:
                # الاستدعاء النخبوي الجديد
                response = client.models.generate_content(
                    model=CONFIG["MODEL_ID"],
                    contents=prompt
                )
                report = response.text
                
                # إرسال البطاقة لتيليغرام
                requests.post(f"https://api.telegram.org/bot{CONFIG['TELEGRAM_TOKEN']}/sendPhoto", 
                             json={"chat_id": CONFIG["TELEGRAM_CHAT_ID"], "photo": deal['image'], "caption": report, "parse_mode": "Markdown"})
                self.log(f"✅ تم الإرسال بنجاح.")
                time.sleep(2)
            except Exception as e:
                self.log(f"خطأ فـ Gemini 3: {e}", "WARNING")

    def run(self):
        try:
            self.init_session()
            self.hunt_listings()
            self.analyze_and_broadcast()
        finally:
            if self.driver: self.driver.quit()
            self.log("نهاية المهمة.")

if __name__ == "__main__":
    EliteGemini3Hunter().run()