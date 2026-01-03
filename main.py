import os
import time
import random
import json
import requests
from seleniumbase import Driver
from groq import Groq
from datetime import datetime

# --- البركوتوكول الأمني والإعدادات ---
CONFIG = {
    "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
    "TELEGRAM_TOKEN": os.getenv("TELEGRAM_TOKEN"),
    "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
    "TARGET_URL": "https://web.facebook.com/marketplace/casablanca/propertyforsale",
    "AI_MODEL": "meta-llama/llama-4-scout-17b-16e-instruct", # الموديل العملاق ديالك
    "MAX_DEALS": 5, # كنركزو على الجودة ماشي الكمية
    "RETRY_ATTEMPTS": 3
}

client = Groq(api_key=CONFIG["GROQ_API_KEY"])

class EliteHunterV4:
    def __init__(self):
        self.driver = None
        self.processed_deals = []

    def log(self, msg, level="INFO"):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{level}] 🛡️ {msg}")

    def boot_system(self):
        """تشغيل المحرك بوضعية التخفي القصوى"""
        self.log("إقلاع المحرك الشبح (UC Mode)...")
        self.driver = Driver(uc=True, headless=True)

    def bypass_security(self):
        """زرع الكوكيز واختراق الجلسة"""
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
            self.log("تم تأكيد الهوية الرقمية بنجاح.")
        except Exception as e:
            self.log(f"خطأ في الكوكيز: {e}", "ERROR")
            raise

    def hunt_marketplace(self):
        """قنص الإعلانات وتنظيمها في هيكل بيانات نظيف"""
        self.log(f"الذهاب للهدف العقاري: {CONFIG['TARGET_URL']}")
        self.driver.get(CONFIG["TARGET_URL"])
        time.sleep(random.uniform(10, 15))
        
        # التمرير (Scrolling) لجلب أحدث الهمزات
        self.driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(3)

        cards = self.driver.find_elements("css selector", 'div[style*="max-width"]')
        self.log(f"تم رصد {len(cards)} إعلان. جاري التصفية النخبوية...")

        for card in cards:
            if len(self.processed_deals) >= CONFIG["MAX_DEALS"]: break
            try:
                # استخراج البيانات الأساسية
                raw_text = card.text.split('\n')
                if len(raw_text) < 2: continue
                
                link = card.find_element("css selector", "a").get_attribute("href").split('?')[0]
                
                deal = {
                    "price": raw_text[0],
                    "title": raw_text[1],
                    "location": raw_text[2] if len(raw_text) > 2 else "غير محدد",
                    "link": link,
                    "timestamp": datetime.now().isoformat()
                }
                self.processed_deals.append(deal)
                self.log(f"تم قنص: {deal['title'][:30]}")
            except: continue

    def analyze_deals_deeply(self):
        """تحليل الصفقات باستعمال Llama-4 Scout (الجدول والتحليل)"""
        if not self.processed_deals:
            return "🤷‍♂️ الساحة خاوية هاد الساعة، ما كاينش همزات."

        self.log(f"بدء التحليل العميق بـ {CONFIG['AI_MODEL']}...")
        deals_json = json.dumps(self.processed_deals, ensure_ascii=False)

        prompt = f"""
        Analyze these Moroccan Real Estate deals: {deals_json}
        
        Task: 
        1. Compare price vs location for each deal.
        2. Create a "Pros & Cons" table for the top 3 deals.
        3. Response must be in Professional Moroccan Business Darija.
        
        Format for each deal:
        💎 **[اسم الهمزة]**
        📊 **تحليل النخبة:** (لماذا هي همزة؟)
        ✅ **المميزات (Pros):** (نقطتين)
        ❌ **العيوب/المخاطر (Cons):** (نقطة واحدة)
        💰 **السعر والموقع:** (بوضوح)
        🔗 **رابط القناص:** [الرابط]
        """

        for i in range(CONFIG["RETRY_ATTEMPTS"]):
            try:
                completion = client.chat.completions.create(
                    messages=[{"role": "system", "content": "You are a Master Moroccan Real Estate Advisor."},
                              {"role": "user", "content": prompt}],
                    model=CONFIG["AI_MODEL"],
                    temperature=0.1 # دقة مطلقة
                )
                return completion.choices[0].message.content
            except Exception as e:
                self.log(f"AI مضغوط، محاولة {i+1}... انتظار 10 ثواني", "WARNING")
                time.sleep(10)
        return "❌ فشل النظام في التواصل مع العقل المدبر."

    def broadcast_report(self, report):
        """إرسال التقرير النهائي المنظم لتيليغرام"""
        url = f"https://api.telegram.org/bot{CONFIG['TELEGRAM_TOKEN']}/sendMessage"
        payload = {
            "chat_id": CONFIG["TELEGRAM_CHAT_ID"], 
            "text": f"🚀 **تقرير القناص النخبوي V4**\n\n{report}", 
            "parse_mode": "Markdown"
        }
        try:
            requests.post(url, json=payload, timeout=10)
            self.log("التقرير مشى لمركز القيادة بنجاح.")
        except Exception as e:
            self.log(f"خطأ في الإرسال لتيليغرام: {e}", "ERROR")

    def execute_mission(self):
        """تشغيل الماكينة من الألف إلى الياء بنظام"""
        try:
            self.boot_system()
            self.bypass_security()
            self.hunt_marketplace()
            report = self.analyze_deals_deeply()
            self.broadcast_report(report)
        except Exception as e:
            self.log(f"انهيار في النظام: {e}", "CRITICAL")
        finally:
            if self.driver:
                self.driver.quit()
                self.log("إغلاق المحرك بسلام.")

if __name__ == "__main__":
    print("--- 🏁 انطلاق النظام النخبوي (The Final System) ---")
    EliteHunterV4().execute_mission()