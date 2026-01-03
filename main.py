import os
import time
import random
import json
import requests
import google.generativeai as genai  # إضافة مكتبة جيميناي
from seleniumbase import Driver
from datetime import datetime

# --- بروتوكول الإعدادات المرجعية ---
CONFIG = {
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
    "TELEGRAM_TOKEN": os.getenv("TELEGRAM_TOKEN"),
    "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
    "TARGET_URL": "https://www.facebook.com/marketplace/fez/propertyrentals/?exact=false",
    "GEMINI_MODEL": "gemini-1.5-flash", 
    "WAIT_TIME": 10
}

# إعداد محرك Gemini
genai.configure(api_key=CONFIG["GEMINI_API_KEY"])
gemini_model = genai.GenerativeModel(CONFIG["GEMINI_MODEL"])

class EliteVisualHunter:
    def __init__(self):
        self.driver = None
        self.deals = []

    def log(self, msg, status="INFO"):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{status}] 🛡️ {msg}")

    def send_telegram_deal(self, caption, photo_url):
        """إرسال كل همزة ببطاقة احترافية (تصويرة + نص)"""
        url = f"https://api.telegram.org/bot{CONFIG['TELEGRAM_TOKEN']}/sendPhoto"
        payload = {
            "chat_id": CONFIG["TELEGRAM_CHAT_ID"],
            "photo": photo_url,
            "caption": caption,
            "parse_mode": "Markdown"
        }
        try:
            requests.post(url, json=payload, timeout=15)
        except Exception as e:
            self.log(f"خطأ في إرسال تيليغرام: {e}", "ERROR")

    def init_session(self):
        """الدخول بوضعية الشبح وزرع الكوكيز"""
        self.driver = Driver(uc=True, headless=True)
        try:
            self.driver.get("https://web.facebook.com")
            with open("cookies.json", "r") as f:
                cookies = json.load(f)
                for cookie in cookies:
                    if 'sameSite' in cookie and cookie['sameSite'] not in ["Strict", "Lax", "None"]:
                        del cookie['sameSite']
                    self.driver.add_cookie(cookie)
            self.driver.refresh()
            time.sleep(5)
            self.log("تم اختراق الجلسة بالكوكيز بنجاح.")
        except Exception as e:
            self.log(f"فشل زرع الكوكيز: {e}", "CRITICAL")
            raise

    def hunt_listings(self):
        """قنص الداتا الخام مع الروابط البصرية"""
        self.log(f"الذهاب للهدف: {CONFIG['TARGET_URL']}")
        self.driver.get(CONFIG["TARGET_URL"])
        time.sleep(random.uniform(10, 15))
        
        self.driver.execute_script("window.scrollTo(0, 800);")
        time.sleep(3)

        cards = self.driver.find_elements("css selector", 'div[style*="max-width"]')
        self.log(f"تم رصد {len(cards)} إعلان. جاري استخراج البيانات...")

        for card in cards[:6]: 
            try:
                img = card.find_element("css selector", "img").get_attribute("src")
                raw_text = card.text.split('\n')
                link = card.find_element("css selector", "a").get_attribute("href").split('?')[0]
                
                if "/marketplace/item/" in link and len(raw_text) >= 2:
                    self.deals.append({
                        "price": raw_text[0],
                        "title": raw_text[1],
                        "location": raw_text[2] if len(raw_text) > 2 else "غير محدد",
                        "link": link,
                        "image": img
                    })
            except: continue
        self.log(f"تم قنص {len(self.deals)} بطاقة منظمة.")

    def analyze_and_broadcast(self):
        """التحليل باستعمال Gemini وإرسال التقرير"""
        for deal in self.deals:
            self.log(f"Gemini كايحلل فـ: {deal['title'][:20]}...")
            
            prompt = f"""
            Analyze this Moroccan property: {json.dumps(deal, ensure_ascii=False)}
            Requirements:
            1. Convert the price to Moroccan 'Million' or stay in 'DH' for rent.
            2. Extract any phone number if present.
            3. Write a high-level Business Darija report.
            Structure:
            💎 **[اسم الهمزة]**
            💰 **الثمن:** [Price]
            📍 **الموقع:** [Location]
            📊 **تحليل النخبة:**
            ✅ **المميزات:**
            ❌ **العيوب:**
            📞 **للتواصل:** [Phone or link]
            🔗 **الرابط:** [Link]
            """

            try:
                # طلب التحليل من Gemini
                response = gemini_model.generate_content(prompt)
                report = response.text
                
                self.send_telegram_deal(report, deal['image'])
                self.log(f"تم إرسال بطاقة {deal['title'][:20]}")
                time.sleep(2) 
            except Exception as e:
                self.log(f"خطأ في تحليل Gemini: {e}", "WARNING")

    def run(self):
        """تشغيل الماكينة بالترتيب المرجعي"""
        try:
            self.init_session()
            self.hunt_listings()
            self.analyze_and_broadcast()
        finally:
            if self.driver: self.driver.quit()
            self.log("نهاية المهمة بنجاح.")

if __name__ == "__main__":
    EliteVisualHunter().run()