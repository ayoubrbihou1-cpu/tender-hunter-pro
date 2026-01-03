import os
import time
import random
import json
import requests
import re
from google import genai  # المكتبة الأحدث لـ 2026
from seleniumbase import Driver
from datetime import datetime

# --- بروتوكول الإعدادات النخبوية ---
CONFIG = {
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
    "TELEGRAM_TOKEN": os.getenv("TELEGRAM_TOKEN"),
    "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
    "TARGET_URL": "https://www.facebook.com/marketplace/fez/propertyrentals/?exact=false",
    "MODEL_ID": "gemini-2.5-flash",  # الموديل القناص
    "WAIT_BETWEEN_DEALS": 65  # حماية الكوطا من RESOURCE_EXHAUSTED
}

# إقلاع محرك Gemini
client = genai.Client(api_key=CONFIG["GEMINI_API_KEY"])

class UltimateEliteHunter:
    def __init__(self):
        self.driver = None
        self.deals = []

    def log(self, msg, status="INFO"):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{status}] 🛡️ {msg}")

    def escape_markdown(self, text):
        """تجهيز النص لتيليغرام: نظام الهروب من الفخاخ"""
        escape_chars = r'_*[]()~`>#+-=|{}.!'
        return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)

    def init_session(self):
        """اختراق الجلسة بوضعية الشبح (UC Mode)"""
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
            self.log("تم تأكيد الهوية الرقمية بنجاح.")
        except Exception as e:
            self.log(f"فشل في زرع الكوكيز: {e}", "CRITICAL")
            raise

    def hunt_listings(self):
        """قنص الهمزات من ماركت بلايس فاس"""
        self.log(f"التوجه للهدف: {CONFIG['TARGET_URL']}")
        self.driver.get(CONFIG["TARGET_URL"])
        time.sleep(15)
        
        # سكرول خفيف باش يبانو الصور والمعلومات
        self.driver.execute_script("window.scrollTo(0, 800);")
        time.sleep(5)

        cards = self.driver.find_elements("css selector", 'div[style*="max-width"]')
        self.log(f"تم رصد {len(cards)} إعلان أولي.")

        # نكتفي بأفضل 3 همزات لضمان جودة التحليل وعدم حرق الكوطا
        for card in cards[:3]:
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
        self.log(f"تم قنص {len(self.deals)} بطاقة منظمة ف الذاكرة.")

    def send_safe_telegram(self, report, photo_url):
        """إرسال ذكي مع فحص الاستجابة لتفادي الميساجات الوهمية"""
        url = f"https://api.telegram.org/bot{CONFIG['TELEGRAM_TOKEN']}/sendPhoto"
        payload = {
            "chat_id": CONFIG["TELEGRAM_CHAT_ID"],
            "photo": photo_url,
            "caption": report,
            "parse_mode": "MarkdownV2"
        }
        try:
            res = requests.post(url, json=payload, timeout=15)
            if res.status_code == 200:
                self.log("✅ التقرير وصل لتيليغرام بنجاح.")
            else:
                self.log(f"❌ فشل الإرسال (Code {res.status_code}). كنحاول نصيفط نص عادي...", "WARNING")
                # Fallback: إرسال نص عادي إذا فشل التنسيق
                requests.post(url, json={
                    "chat_id": CONFIG["TELEGRAM_CHAT_ID"],
                    "photo": photo_url,
                    "caption": f"⚠️ همزة جديدة (تنسيق مبسط):\n{report.replace('\\', '')}"
                })
        except Exception as e:
            self.log(f"خطأ تقني ف تيليغرام: {e}", "ERROR")

    def analyze_and_broadcast(self):
        """التحليل النخبوي بـ Gemini 2.5 Flash"""
        for i, deal in enumerate(self.deals):
            self.log(f"بدء تحليل الهمزة {i+1}/{len(self.deals)}...")
            
            prompt = f"""
            Analyze this Moroccan property: {json.dumps(deal, ensure_ascii=False)}
            Convert price to 'Million' (e.g. 1500 DH -> 1500 درهم للكراء).
            Write a Professional Business Darija report.
            Structure:
            💎 *[Title]*
            💰 *Price*
            📍 *Location*
            📊 *Elite Analysis* (Why it's a deal?)
            ✅ *Pros*
            ❌ *Cons*
            🔗 *Link*
            """

            try:
                response = client.models.generate_content(
                    model=CONFIG["MODEL_ID"],
                    contents=prompt
                )
                raw_report = response.text
                
                # تنظيف النص من الرموز القاتلة
                safe_report = self.escape_markdown(raw_report)
                
                # الإرسال الفعلي
                self.send_safe_telegram(safe_report, deal['image'])
                
                # راحة إجبارية لتفادي RESOURCE_EXHAUSTED
                self.log(f"انتظار {CONFIG['WAIT_BETWEEN_DEALS']} ثانية لحماية الكوطا...")
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
            self.log("نهاية المهمة بنجاح.")

if __name__ == "__main__":
    UltimateEliteHunter().run()