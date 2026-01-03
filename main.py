import os
import time
import random
import json
import requests
from seleniumbase import Driver
from groq import Groq
from datetime import datetime

# --- بروتوكول الإعدادات العليا ---
CONFIG = {
    "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
    "TELEGRAM_TOKEN": os.getenv("TELEGRAM_TOKEN"),
    "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
    "TARGET_URL": "https://web.facebook.com/marketplace/casablanca/propertyforsale",
    "AI_MODEL": "meta-llama/llama-4-scout-17b-16e-instruct" # الموديل المعتمد
}

client = Groq(api_key=CONFIG["GROQ_API_KEY"])

class EliteLlamaSystem:
    def __init__(self):
        self.driver = None
        self.valid_samesite = ["Strict", "Lax", "None"]

    def log(self, action, status="DEBUG"):
        """نظام تتبع احترافي"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{status}] 🛡️ {action}")

    def boot_and_inject(self):
        """إقلاع المحرك الشبح وزرع الهوية الرقمية المنظفة"""
        self.log("إقلاع المحرك بوضعية UC...")
        self.driver = Driver(uc=True, headless=True)
        try:
            self.driver.get("https://web.facebook.com")
            # تنظيف الكوكيز حبة حبة لتفادي AssertionError
            with open("cookies.json", "r") as f:
                cookies = json.load(f)
                for c in cookies:
                    if 'sameSite' in c and c['sameSite'] not in self.valid_samesite:
                        del c['sameSite']
                    try: self.driver.add_cookie(c)
                    except: continue
            self.driver.refresh()
            time.sleep(5)
            self.driver.save_screenshot("debug_1_auth.png")
            self.log("تم اختراق الجلسة. سكرين شوت (1) واجدة.")
        except Exception as e:
            self.log(f"خطأ في زرع الكوكيز: {e}", "ERROR")

    def run_clean_mission(self):
        """مهمة قنص منظمة بنظام الـ JSON المعزول"""
        self.log(f"التوجه للماركت بلايس: {CONFIG['TARGET_URL']}")
        self.driver.get(CONFIG["TARGET_URL"])
        time.sleep(12) # انتظار لضمان التحميل الكامل
        self.driver.save_screenshot("debug_2_marketplace.png")

        # المرحلة 1: القنص الأولي وفصل البيانات (Decoupling)
        # كنهزو الروابط فـ لستة باش نقتلو stale element reference نهائياً
        listing_cards = self.driver.find_elements("css selector", 'div[style*="max-width"]')[:3]
        pre_hunt_list = []

        for card in listing_cards:
            try:
                pre_hunt_list.append({
                    "cover": card.find_element("css selector", "img").get_attribute("src"),
                    "link": card.find_element("css selector", "a").get_attribute("href"),
                    "title": card.text.split('\n')[1] if len(card.text.split('\n')) > 1 else "عقار مغربي"
                })
            except: continue

        self.log(f"تم تخزين {len(pre_hunt_list)} روابط بنجاح. بادي الفحص العميق...")

        # المرحلة 2: الفحص العميق وبناء ملف JSON لكل إعلان
        for i, item in enumerate(pre_hunt_list):
            try:
                self.log(f"دخول عميق للإعلان {i+1}: {item['title'][:25]}...")
                self.driver.get(item['link'])
                time.sleep(10) # وقت كافي لظهور الصور الداخلية
                self.driver.save_screenshot(f"debug_3_item_{i+1}.png")

                # قنص الصور وتصفية الروابط لتفادي Error 400
                raw_imgs = self.driver.find_elements("css selector", 'img[src*="fbcdn"]')
                photos_json = []
                for img in raw_imgs:
                    src = img.get_attribute("src")
                    if src and src.startswith("http") and src not in photos_json:
                        photos_json.append(src)
                
                final_photos = photos_json[:6] # نكتفي بـ 6 صور للتحليل الدقيق

                # إذا لم يجد صورا داخلية، يستخدم صورة الكوفر
                if not final_photos: final_photos = [item['cover']]

                # تجميع البيانات في ملف JSON "افتراضي" لإرساله لـ Groq
                deal_package = {
                    "property_id": i+1,
                    "title": item["title"],
                    "link": item["link"].split('?')[0],
                    "images": final_photos,
                    "timestamp": datetime.now().isoformat()
                }

                self.analyze_and_broadcast(deal_package)
                
            except Exception as e:
                self.log(f"فشل في معالجة الإعلان {i+1}: {e}", "ERROR")

    def analyze_and_broadcast(self, deal_json):
        """إرسال ملف الـ JSON المنظم لـ Llama-4 Scout والتحليل النخبوي"""
        self.log(f"إرسال JSON الصفقة {deal_json['property_id']} لـ AI...")
        
        # تحويل الداتا لـ JSON String نقي بلا أخطاء
        formatted_json = json.dumps(deal_json, ensure_ascii=False, indent=2)
        
        img_payload = [{"type": "image_url", "image_url": {"url": url}} for url in deal_json["images"]]
        
        prompt = f"""
        Analyze this property data provided in JSON format:
        {formatted_json}

        Required output in Moroccan Business Darija:
        1. Convert price to 'Million' (e.g., 600,000 DH -> 60 مليون).
        2. Detailed 'Finition' analysis based on all images.
        3. Pros & Cons Table.
        4. Clear Link in the end.
        """
        
        try:
            completion = client.chat.completions.create(
                messages=[{"role": "user", "content": [{"type": "text", "text": prompt}] + img_payload}],
                model=CONFIG["AI_MODEL"],
                temperature=0.1 # دقة رياضية
            )
            report = completion.choices[0].message.content
            
            # إرسال البطاقة النهائية لتيليغرام
            requests.post(f"https://api.telegram.org/bot{CONFIG['TELEGRAM_TOKEN']}/sendPhoto", 
                         json={"chat_id": CONFIG["TELEGRAM_CHAT_ID"], "photo": deal_json["images"][0], "caption": report, "parse_mode": "Markdown"})
            self.log(f"✅ تم إرسال التقرير {deal_json['property_id']} بنجاح.")
        except Exception as e:
            self.log(f"خطأ في تواصل AI: {e}", "ERROR")

    def execute_one_shot(self):
        """تنفيذ العملية كاملة لمرة واحدة"""
        try:
            self.boot_and_inject()
            self.run_clean_mission()
        finally:
            if self.driver:
                self.driver.quit()
                self.log("إغلاق المحرك بسلام. انتهت المهمة.")

if __name__ == "__main__":
    print("--- 🏁 انطلاق نظام Llama-4 Scout النخبوي (JSON Edition) ---")
    EliteLlamaSystem().execute_one_shot()