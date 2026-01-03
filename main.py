import os
import time
import random
import json
import requests
from seleniumbase import Driver
from groq import Groq
from datetime import datetime

# --- الإعدادات النخبوية (v3.0) ---
CONFIG = {
    "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
    "TELEGRAM_TOKEN": os.getenv("TELEGRAM_TOKEN"),
    "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
    "TARGET_URL": "https://web.facebook.com/marketplace/casablanca/propertyforsale",
    "AI_MODEL": "meta-llama/llama-4-scout-17b-16e-instruct", # الموديل الجديد ديالك
    "MAX_RETRIES": 3,  # عدد محاولات التواصل مع AI في حالة الضغط
    "WAIT_TIME": 10    # ثواني الانتظار بين المحاولات
}

client = Groq(api_key=CONFIG["GROQ_API_KEY"])

class EliteRealEstateHunter:
    def __init__(self):
        self.driver = None
        self.raw_data = []

    def log(self, action, status="INFO"):
        """نظام تتبع احترافي للعمليات"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{status}] 🛠️ {action}")

    def start_engine(self):
        """تشغيل المتصفح بوضعية الشبح المتطورة"""
        self.log("إقلاع المحرك بوضعية التخفي UC...")
        self.driver = Driver(uc=True, headless=True)

    def session_hijack(self):
        """زرع الكوكيز لتجاوز جدار الحماية"""
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
            self.log("تم اختراق الجلسة بنجاح واسترجاع الهوية.")
        except Exception as e:
            self.log(f"فشل في زرع الكوكيز: {e}", "ERROR")
            raise

    def capture_listings(self):
        """قنص البيانات الخام وتنظيفها قبل التحليل"""
        self.log(f"الذهاب للهدف: {CONFIG['TARGET_URL']}")
        self.driver.get(CONFIG["TARGET_URL"])
        
        # انتظار عشوائي لتجنب البلوك
        time.sleep(random.uniform(10, 20))
        
        cards = self.driver.find_elements("css selector", 'div[style*="max-width"]')
        self.log(f"تم رصد {len(cards)} إعلان محتمل.")

        for card in cards[:12]:
            try:
                # استخراج النصوص والصورة (للتحليل البصري مستقبلاً)
                lines = card.text.split('\n')
                link = card.find_element("css selector", "a").get_attribute("href").split('?')[0]
                
                # تنظيم الداتا في هيكل JSON نظيف
                self.raw_data.append({
                    "title": lines[1] if len(lines) > 1 else "بدون عنوان",
                    "price": lines[0],
                    "location": lines[2] if len(lines) > 2 else "غير محدد",
                    "link": link
                })
            except: continue
        self.log(f"تم تنظيف {len(self.raw_data)} إعلان بنجاح.")

    def analyze_with_scout(self):
        """تحليل البيانات باستخدام Llama-4-Scout مع بروتوكول الانتظار"""
        if not self.raw_data:
            return "🤷‍♂️ لم يتم العثور على بيانات في هذه الدورة."

        self.log(f"بدء التحليل باستخدام {CONFIG['AI_MODEL']}...")
        formatted_json = json.dumps(self.raw_data, ensure_ascii=False)

        prompt = f"""
        Analyze these Moroccan real estate listings: {formatted_json}
        Identify the Top 3 "Hamzat" based on price/location.
        Respond in high-level Moroccan Business Darija.
        Format: 
        🏠 Title
        💰 Analysis of Price (Comparison)
        🔗 Link
        """

        for attempt in range(CONFIG["MAX_RETRIES"]):
            try:
                # طلب التحليل من Groq
                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=CONFIG["AI_MODEL"],
                    temperature=0.1 # دقة عالية جداً
                )
                return completion.choices[0].message.content
            except Exception as e:
                self.log(f"محاولة {attempt + 1} فشلت: AI يحتاج وقت للتفكير. الانتظار {CONFIG['WAIT_TIME']} ثواني...", "WARNING")
                time.sleep(CONFIG["WAIT_TIME"])
        
        return "❌ فشل النظام في الحصول على تحليل بعد عدة محاولات."

    def broadcast(self, report):
        """إرسال النتيجة النهائية لمركز القيادة في تيليغرام"""
        url = f"https://api.telegram.org/bot{CONFIG['TELEGRAM_TOKEN']}/sendMessage"
        payload = {
            "chat_id": CONFIG["TELEGRAM_CHAT_ID"], 
            "text": f"💎 **تقرير القناص النخبوي (Llama-4 Scout)**\n\n{report}", 
            "parse_mode": "Markdown"
        }
        try:
            requests.post(url, json=payload, timeout=10)
            self.log("تم إرسال التقرير بنجاح لتيليغرام.")
        except Exception as e:
            self.log(f"خطأ في الإرسال: {e}", "ERROR")

    def run_mission(self):
        """تشغيل العملية المتكاملة من الألف إلى الياء"""
        try:
            self.start_engine()
            self.session_hijack()
            self.capture_listings()
            final_report = self.analyze_with_scout()
            self.broadcast(final_report)
        finally:
            if self.driver:
                self.driver.quit()
                self.log("إغلاق المحرك بسلام.")

if __name__ == "__main__":
    print("--- 🏁 انطلاق المهمة النخبوية ---")
    Hunter = EliteRealEstateHunter()
    Hunter.run_mission()