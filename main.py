import os
import time
import json
import requests
from google import genai # المكتبة الجديدة كلياً
from seleniumbase import Driver
from datetime import datetime

# --- بروتوكول الإعدادات العليا ---
CONFIG = {
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
    "TELEGRAM_TOKEN": os.getenv("TELEGRAM_TOKEN"),
    "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
    "TARGET_URL": "https://www.facebook.com/marketplace/fez/propertyrentals/?exact=false",
    "MODEL_ID": "gemini-2.5-flash", # الموديل المعتمد فـ الصورة
    "WAIT_BETWEEN_DEALS": 65 # نظام حماية الكوطا
}

# إقلاع عميل Gemini بالطريقة الجديدة
client = genai.Client(api_key=CONFIG["GEMINI_API_KEY"])

class UltimateGeminiHunter:
    def __init__(self):
        self.driver = None
        self.deals = []

    def log(self, msg, status="INFO"):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{status}] 🛡️ {msg}")

    def init_session(self):
        """إقلاع المحرك واختراق الجلسة"""
        self.log("إقلاع المحرك UC Mode...")
        self.driver = Driver(uc=True, headless=True)
        try:
            self.driver.get("https://web.facebook.com")
            with open("cookies.json", "r") as f:
                cookies = json.load(f)
                for c in cookies:
                    # تنظيف الكوكيز لتفادي AssertionError
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
        
        cards = self.driver.find_elements("css selector", 'div[style*="max-width"]')[:3] # نكتفي بـ 3 همزات لضمان الجودة
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

    def analyze_and_broadcast(self):
        """التحليل باستعمال Gemini 2.5 Flash الجديد"""
        for i, deal in enumerate(self.deals):
            self.log(f"بدء تحليل الهمزة {i+1}/{len(self.deals)}...")
            
            prompt = f"""
            Analyze this property data: {json.dumps(deal, ensure_ascii=False)}
            Convert price to 'Million' (Moroccan), check location, and write a Professional Business Darija report.
            Format:
            💎 **[اسم العقار]**
            💰 **الثمن بالملايين:** [Price]
            📊 **تحليل النخبة:** [Why it's a deal?]
            ✅ **المميزات:**
            ❌ **العيوب:**
            🔗 **الرابط:** [Link]
            """
            
            try:
                # الاستدعاء النخبوي الجديد من الصورة
                response = client.models.generate_content(
                    model=CONFIG["MODEL_ID"],
                    contents=prompt
                )
                report = response.text
                
                # إرسال لتيليغرام
                requests.post(f"https://api.telegram.org/bot{CONFIG['TELEGRAM_TOKEN']}/sendPhoto", 
                             json={"chat_id": CONFIG["TELEGRAM_CHAT_ID"], "photo": deal['image'], "caption": report, "parse_mode": "Markdown"})
                
                self.log(f"✅ تم الإرسال. انتظار {CONFIG['WAIT_BETWEEN_DEALS']} ثانية لحماية الكوطا...")
                time.sleep(CONFIG["WAIT_BETWEEN_DEALS"]) # راحة إجبارية

            except Exception as e:
                if "429" in str(e):
                    self.log("🛑 وصلنا لسقف RESOURCE_EXHAUSTED. غانحبسو الدورة دابا.", "WARNING")
                    break 
                self.log(f"خطأ تقني: {e}", "ERROR")

    def run(self):
        """المحرك الأساسي"""
        try:
            self.init_session()
            self.hunt_listings()
            self.analyze_and_broadcast()
        finally:
            if self.driver: self.driver.quit()
            self.log("نهاية المهمة بنجاح.")

if __name__ == "__main__":
    UltimateGeminiHunter().run()