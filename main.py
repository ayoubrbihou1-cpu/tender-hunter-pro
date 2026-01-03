import os
import time
import random
import json
import requests
from seleniumbase import Driver
from groq import Groq
from datetime import datetime

# --- إعدادات مركز العمليات ---
CONFIG = {
    "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
    "TELEGRAM_TOKEN": os.getenv("TELEGRAM_TOKEN"),
    "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
    "TARGET_URL": "https://web.facebook.com/marketplace/casablanca/propertyforsale",
    "AI_MODEL": "meta-llama/llama-4-scout-17b-16e-instruct"
}

client = Groq(api_key=CONFIG["GROQ_API_KEY"])

class UltimateLlamaHunter:
    def __init__(self):
        self.driver = None
        self.valid_samesite = ["Strict", "Lax", "None"]

    def log(self, action, status="DEBUG"):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{status}] 🛡️ {action}")

    def boot_and_inject(self):
        """إقلاع المحرك الشبح وزرع الهوية الرقمية"""
        self.log("إقلاع المحرك UC Mode...")
        self.driver = Driver(uc=True, headless=True)
        try:
            self.driver.get("https://web.facebook.com")
            # تنظيف الكوكيز لتفادي انهيار المتصفح
            with open("cookies.json", "r") as f:
                cookies = json.load(f)
                for c in cookies:
                    if 'sameSite' in c and c['sameSite'] not in self.valid_samesite:
                        del c['sameSite']
                    try: self.driver.add_cookie(c)
                    except: continue
            self.driver.refresh()
            time.sleep(5)
            self.driver.save_screenshot("debug_1_session.png")
            self.log("تم زرع الكوكيز. سكرين شوت (1) واجدة.")
        except Exception as e:
            self.log(f"خطأ فـ الكوكيز: {e}", "ERROR")

    def run_safe_mission(self):
        """مهمة قنص منظمة بلا تداخل معلومات"""
        self.log(f"التوجه للهدف: {CONFIG['TARGET_URL']}")
        self.driver.get(CONFIG["TARGET_URL"])
        time.sleep(12)
        self.driver.save_screenshot("debug_2_marketplace.png")

        # 1. جمع الروابط أولاً (Decoupling) لقتل stale element reference
        cards = self.driver.find_elements("css selector", 'div[style*="max-width"]')[:3]
        mission_list = []

        for card in cards:
            try:
                mission_list.append({
                    "cover": card.find_element("css selector", "img").get_attribute("src"),
                    "link": card.find_element("css selector", "a").get_attribute("href"),
                    "title": card.text.split('\n')[1] if len(card.text.split('\n')) > 1 else "عقار"
                })
            except: continue

        self.log(f"تم تخزين {len(mission_list)} روابط. بادي الفحص العميق...")

        # 2. معالجة كل رابط من القائمة المعزولة
        for i, item in enumerate(mission_list):
            try:
                self.log(f"فحص الإعلان {i+1}: {item['title'][:20]}")
                self.driver.get(item['link'])
                time.sleep(10) # انتظار لضمان تحميل الصور
                self.driver.save_screenshot(f"debug_3_item_{i+1}.png")

                # قنص الصور الداخلية وتصفية الروابط لتفادي Error 400
                raw_imgs = self.driver.find_elements("css selector", 'img[src*="fbcdn"]')
                clean_photos = []
                for img in raw_imgs:
                    src = img.get_attribute("src")
                    if src and src.startswith("http") and src not in clean_photos:
                        clean_photos.append(src)
                
                final_photos = clean_photos[:6]

                # Fallback: إذا فشل تحميل الصور لداخل، خدم بـ Cover
                if not final_photos:
                    final_photos = [item['cover']]

                if final_photos:
                    self.analyze_and_report(final_photos, item['link'], item['title'])
                
            except Exception as e:
                self.log(f"فشل فـ معالجة الإعلان {i+1}: {e}", "ERROR")

    def analyze_and_report(self, photos, link, title):
        """تحليل نخبوي باستعمال Llama-4 Scout وإرسال لتيليغرام"""
        self.log(f"AI كايحلل {len(photos)} صورة دابا...")
        
        # تنظيم payload الصور لـ Groq بلا غلط
        img_payload = [{"type": "image_url", "image_url": {"url": url}} for url in photos]
        
        prompt = f"""
        حلل هاد العقار ({title}) باستعمال كاع الصور.
        المطلوب بالدارجة المغربية (Business Darija):
        1. حول الثمن لـ 'مليون' (مثلا 950,000 DH تولي 95 مليون).
        2. تحليل جودة الفينيسيون (الزليج، الصباغة، الكوزينة).
        3. جدول Pros & Cons بوضوح.
        4. الرابط فـ النهاية: {link.split('?')[0]}
        """
        
        try:
            completion = client.chat.completions.create(
                messages=[{"role": "user", "content": [{"type": "text", "text": prompt}] + img_payload}],
                model=CONFIG["AI_MODEL"],
                temperature=0.1
            )
            report = completion.choices[0].message.content
            
            # إرسال البطاقة لتيليغرام
            requests.post(f"https://api.telegram.org/bot{CONFIG['TELEGRAM_TOKEN']}/sendPhoto", 
                         json={"chat_id": CONFIG["TELEGRAM_CHAT_ID"], "photo": photos[0], "caption": report, "parse_mode": "Markdown"})
            self.log("✅ التقرير مشى لتيليغرام بنجاح.")
        except Exception as e:
            self.log(f"خطأ AI: {e}", "ERROR")

    def execute(self):
        try:
            self.boot_and_inject()
            self.run_safe_mission()
        finally:
            if self.driver:
                self.driver.quit()
                self.log("انتهت المهمة. إغلاق المتصفح.")

if __name__ == "__main__":
    print("--- 🏁 انطلاق المهمة النخبوية V8.3 ---")
    UltimateLlamaHunter().execute()