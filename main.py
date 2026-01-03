import os
import time
import json
import requests
import google.generativeai as genai # المحرك الوحيد دابا
from seleniumbase import Driver
from datetime import datetime

# --- إعدادات مركز القيادة (Gemini Edition) ---
CONFIG = {
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
    "TELEGRAM_TOKEN": os.getenv("TELEGRAM_TOKEN"),
    "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
    "TARGET_URL": "https://www.facebook.com/marketplace/fez/propertyrentals/?exact=false",
    "GEMINI_MODEL": "gemini-1.5-flash" # القناص السريع
}

# إعداد محرك Gemini
genai.configure(api_key=CONFIG["GEMINI_API_KEY"])
model = genai.GenerativeModel(CONFIG["GEMINI_MODEL"])

class PureGeminiHunter:
    def __init__(self):
        self.driver = None
        self.valid_samesite = ["Strict", "Lax", "None"]

    def log(self, action, status="INFO"):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{status}] 🛡️ {action}")

    def boot_and_auth(self):
        """إقلاع المحرك UC Mode وزرع الهوية الرقمية"""
        self.log("إقلاع المحرك الشبح...")
        self.driver = Driver(uc=True, headless=True)
        try:
            self.driver.get("https://web.facebook.com")
            # تنظيف الكوكيز لتفادي AssertionError
            with open("cookies.json", "r") as f:
                cookies = json.load(f)
                for c in cookies:
                    if 'sameSite' in c and c['sameSite'] not in self.valid_samesite:
                        del c['sameSite']
                    try: self.driver.add_cookie(c)
                    except: continue
            self.driver.refresh()
            time.sleep(5)
            self.log("تم اختراق الجلسة بنجاح.")
        except Exception as e:
            self.log(f"خطأ في الكوكيز: {e}", "ERROR")

    def run_safe_mission(self):
        """دورة قنص منظمة بنظام الـ JSON المعزول"""
        self.log(f"التوجه للماركت بلايس: {CONFIG['TARGET_URL']}")
        self.driver.get(CONFIG["TARGET_URL"])
        time.sleep(12)
        
        # 1. جمع الروابط أولاً (Decoupling) لتفادي stale element
        cards = self.driver.find_elements("css selector", 'div[style*="max-width"]')[:4]
        mission_list = []

        for card in cards:
            try:
                mission_list.append({
                    "cover": card.find_element("css selector", "img").get_attribute("src"),
                    "link": card.find_element("css selector", "a").get_attribute("href"),
                    "title": card.text.split('\n')[1] if len(card.text.split('\n')) > 1 else "عقار مغربي"
                })
            except: continue

        self.log(f"تم تخزين {len(mission_list)} روابط فـ الذاكرة.")

        # 2. الفحص العميق والتحليل بـ Gemini
        for i, item in enumerate(mission_list):
            try:
                self.log(f"فحص الهمزة {i+1}: {item['title'][:25]}...")
                self.driver.get(item['link'])
                time.sleep(10)
                
                # قنص الصور وتصفية الروابط لتفادي الأخطاء البصرية
                img_elements = self.driver.find_elements("css selector", 'img[src*="fbcdn"]')
                clean_photos = []
                for img in img_elements:
                    src = img.get_attribute("src")
                    if src and src.startswith("http") and src not in clean_photos:
                        clean_photos.append(src)
                
                final_photos = clean_photos[:5] if clean_photos else [item['cover']]
                
                # بناء الـ Payload لـ Gemini
                self.analyze_with_gemini(final_photos, item['link'], item['title'])
                
            except Exception as e:
                self.log(f"فشل في معالجة الإعلان {i+1}: {e}", "ERROR")

    def analyze_with_gemini(self, photos, link, title):
        """التحليل النخبوي باستعمال Gemini Vision"""
        self.log(f"Gemini كايحلل {len(photos)} صورة دابا...")
        
        # تحضير الصور للتحليل (Gemini يدعم الروابط المباشرة في بعض البيئات أو يتطلب التحميل)
        # هنا سنعتمد على التحليل النصي والروابط لتسهيل العملية
        prompt = f"""
        أنت مستشار عقاري مغربي نخبوي. حلل هاد العقار من خلال هاد المعلومات:
        العنوان: {title}
        الرابط: {link}
        الصور المرفقة: {photos}

        المطلوب بالدارجة المغربية المجهدة:
        1. حول الثمن لـ 'مليون' (مثلا 2500 DH تولي 2500 درهم للكراء أو الملايين للبيع).
        2. جدول Pros & Cons بوضوح.
        3. رأيك واش هادي 'همزة' حقيقية فـ فاس.
        4. الرابط بوضوح فـ النهاية.
        """
        
        try:
            response = model.generate_content(prompt)
            report = response.text
            
            # إرسال التقرير لتيليغرام
            requests.post(f"https://api.telegram.org/bot{CONFIG['TELEGRAM_TOKEN']}/sendPhoto", 
                         json={"chat_id": CONFIG["TELEGRAM_CHAT_ID"], "photo": photos[0], "caption": report, "parse_mode": "Markdown"})
            self.log("✅ التقرير مشى لتيليغرام.")
        except Exception as e:
            self.log(f"خطأ فـ Gemini: {e}", "ERROR")

    def execute(self):
        try:
            self.boot_and_inject()
            self.run_safe_mission()
        finally:
            if self.driver: self.driver.quit()
            self.log("إغلاق المحرك. انتهت المهمة.")

if __name__ == "__main__":
    PureGeminiHunter().execute()