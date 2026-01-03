import os
import time
import random
import json
import requests
from seleniumbase import Driver
from groq import Groq
from datetime import datetime

# --- إعدادات مركز القيادة ---
CONFIG = {
    "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
    "TELEGRAM_TOKEN": os.getenv("TELEGRAM_TOKEN"),
    "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
    "TARGET_URL": "https://web.facebook.com/marketplace/casablanca/propertyforsale",
    "AI_MODEL": "meta-llama/llama-4-scout-17b-16e-instruct" # الموديل المعتمد
}

client = Groq(api_key=CONFIG["GROQ_API_KEY"])

class UltimateBulletproofHunter:
    def __init__(self):
        self.driver = None
        self.valid_samesite = ["Strict", "Lax", "None"]

    def log(self, action, status="DEBUG"):
        """نظام تتبع العمليات النخبوي"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{status}] 🛡️ {action}")

    def boot_and_inject(self):
        """إقلاع المحرك واختراق الجلسة"""
        self.log("إقلاع المحرك UC Mode...")
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
            self.log(f"خطأ فادح في الكوكيز: {e}", "ERROR")

    def run_safe_mission(self):
        """دورة قنص منظمة بلا تداخل معلومات"""
        self.log(f"التوجه للماركت بلايس: {CONFIG['TARGET_URL']}")
        self.driver.get(CONFIG["TARGET_URL"])
        time.sleep(12)
        
        # 1. القنص الأولي (Decoupling) لتفادي stale element
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

        self.log(f"تم تخزين {len(mission_list)} روابط. بادي الفحص العميق...")

        # 2. معالجة كل رابط من القائمة المعزولة
        for i, item in enumerate(mission_list):
            try:
                self.log(f"فحص الهمزة {i+1}: {item['title'][:25]}...")
                self.driver.get(item['link'])
                time.sleep(10) # وقت كافي لتحميل الصور
                
                # قنص الصور وتصفية الروابط لتفادي Error 400
                img_elements = self.driver.find_elements("css selector", 'img[src*="fbcdn"]')
                clean_photos = []
                for img in img_elements:
                    src = img.get_attribute("src")
                    # نقبل فقط روابط http الحقيقية ونرفض Base64
                    if src and src.startswith("http") and src not in clean_photos:
                        clean_photos.append(src)
                
                final_photos = clean_photos[:6]

                # Fallback: إذا لم يجد صورا داخلية، يستخدم صورة الكوفر
                if not final_photos: final_photos = [item['cover']]

                # بناء باكيج JSON نقي للإرسال
                deal_package = {
                    "id": i+1,
                    "title": item["title"],
                    "images": final_photos,
                    "link": item["link"].split('?')[0]
                }

                if deal_package["images"]:
                    self.process_with_llama(deal_package)
                
            except Exception as e:
                self.log(f"فشل في معالجة الإعلان {i+1}: {e}", "ERROR")

    def process_with_llama(self, data):
        """تحليل نخبوي باستعمال Llama-4 Scout وإرسال لتيليغرام"""
        self.log(f"AI كايحلل {len(data['images'])} صورة لـ JSON الصفقة {data['id']}...")
        
        # تنظيم payload الصور لـ Groq بلا غلط
        img_payload = [{"type": "image_url", "image_url": {"url": url}} for url in data['images']]
        
        prompt = f"""
        Analyze this property data provided in JSON: {json.dumps(data, ensure_ascii=False)}
        
        Required in Moroccan Business Darija:
        1. Convert price to 'Million' (e.g. 550,000 DH -> 55 مليون).
        2. Detailed Finition analysis from images.
        3. Table of Pros & Cons.
        4. Link: {data['link']}
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
                         json={"chat_id": CONFIG["TELEGRAM_CHAT_ID"], "photo": data['images'][0], "caption": report, "parse_mode": "Markdown"})
            self.log(f"✅ تم إرسال التقرير {data['id']} بنجاح.")
        except Exception as e:
            self.log(f"خطأ فـ AI: {e}", "ERROR")

    def execute(self):
        try:
            self.boot_and_inject()
            self.run_safe_mission()
        finally:
            if self.driver:
                self.driver.quit()
                self.log("إغلاق المحرك. انتهت المهمة.")

if __name__ == "__main__":
    print("--- 🏁 انطلاق النظام الفولاذي V9.1 ---")
    UltimateBulletproofHunter().execute()