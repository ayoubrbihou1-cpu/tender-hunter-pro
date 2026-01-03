import os
import time
import json
import requests
import html 
import re
from google import genai
from google.genai import types 
from seleniumbase import Driver
from datetime import datetime

# --- بروتوكول الإعدادات العليا النخبوية ---
CONFIG = {
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
    "TELEGRAM_TOKEN": os.getenv("TELEGRAM_TOKEN"),
    "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
    "TARGET_URL": "https://www.facebook.com/marketplace/fez/propertyrentals/?exact=false",
    "MODEL_ID": "gemini-2.5-flash", 
    "MAX_DEALS_PER_RUN": 2, # الحفاظ على الكوطا
    "WAIT_BETWEEN_DEALS": 80, # أمان إضافي لتفادي 429
    "DB_FILE": "processed_deals.txt"
}

client = genai.Client(api_key=CONFIG["GEMINI_API_KEY"])

class GrandmasterScout:
    def __init__(self):
        self.driver = None
        self.deals = []
        self.processed_ids = self.load_processed_ids()

    def log(self, msg, status="INFO"):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{status}] 🛡️ {msg}")

    def load_processed_ids(self):
        """تحميل الذاكرة من الملف لتفادي التكرار نهائياً"""
        if os.path.exists(CONFIG["DB_FILE"]):
            with open(CONFIG["DB_FILE"], "r") as f:
                return set(line.strip() for line in f)
        return set()

    def save_id(self, item_id):
        """تسجيل الهمزة ف الذاكرة"""
        with open(CONFIG["DB_FILE"], "a") as f:
            f.write(f"{item_id}\n")
        self.processed_ids.add(item_id)

    def clean_fb_link(self, raw_link):
        match = re.search(r'/item/(\d+)', raw_link)
        if match:
            return match.group(1), f"https://www.facebook.com/marketplace/item/{match.group(1)}/"
        return None, raw_link

    def init_session(self):
        self.log("إقلاع المحرك الإمبراطوري V20.0...")
        self.driver = Driver(uc=True, headless=True)
        try:
            self.driver.get("https://web.facebook.com")
            with open("cookies.json", "r") as f:
                for c in json.load(f):
                    if 'sameSite' in c and c['sameSite'] not in ["Strict", "Lax", "None"]: del c['sameSite']
                    try: self.driver.add_cookie(c)
                    except: continue
            self.driver.refresh()
            time.sleep(5)
            self.log("تم اختراق الجلسة بالكوكيز.")
        except Exception as e:
            self.log(f"فشل الجلسة: {e}", "CRITICAL")
            raise

    def hunt_listings(self):
        self.log(f"التوجه للهدف النخبوي: {CONFIG['TARGET_URL']}")
        self.driver.get(CONFIG["TARGET_URL"])
        time.sleep(15)
        self.driver.execute_script("window.scrollTo(0, 1000);")
        time.sleep(5)
        
        cards = self.driver.find_elements("css selector", 'div[style*="max-width"]')[:6]
        for card in cards:
            try:
                link_elem = card.find_element("css selector", "a")
                item_id, clean_link = self.clean_fb_link(link_elem.get_attribute("href"))
                
                # التحقق من الذاكرة (فقط الجديد يدخل)
                if item_id and item_id not in self.processed_ids:
                    self.deals.append({"id": item_id, "link": clean_link})
                    if len(self.deals) >= CONFIG["MAX_DEALS_PER_RUN"]: break
            except: continue
        self.log(f"تم حجز {len(self.deals)} همزات جديدة كلياً.")

    def analyze_and_broadcast(self):
        for i, deal in enumerate(self.deals):
            try:
                self.log(f"تحليل جراحي للهمزة {i+1}: {deal['link']}")
                self.driver.get(deal['link'])
                time.sleep(12)

                # استخراج الصورة الحقيقية (تجنب تكرار image_a0f1ce)
                try:
                    main_img = self.driver.find_element("css selector", "div[role='main'] img[src*='fbcdn']").get_attribute("src")
                except:
                    main_img = self.driver.find_element("css selector", "img[cursor='pointer']").get_attribute("src")

                # فتح الوصف الكامل (Voir plus)
                try:
                    see_more = self.driver.find_element("xpath", "//span[contains(text(), 'Voir plus') or contains(text(), 'See more') or contains(text(), 'عرض المزيد')]")
                    self.driver.execute_script("arguments[0].click();", see_more)
                    time.sleep(2)
                except: pass

                # جلب الوصف بدقة عالية
                desc_elements = self.driver.find_elements("css selector", "span[dir='auto'], div[dir='auto']")
                full_desc = " ".join([el.text for el in desc_elements if len(el.text) > 40])
                if not full_desc: full_desc = "الوصف غير متوفر."

                # برومبت المرشد الأعظم (التحليل النخبوي 0.001%)
                elite_prompt = f"""
                أنت 'المرشد الأعظم' خبير العقارات في المغرب. حلل بذكاء وبدارجة مغربية مجهدة:
                الوصف: {full_desc[:1200]}

                المطلوب (تقرير مركز تحت 800 حرف):
                💎 <b>[عنوان نخبوي]</b>
                💰 <b>الثمن بالملايين:</b> [حول الثمن بدقة]
                📍 <b>الموقع:</b> [الحي]
                📞 <b>الهاتف:</b> [استخرجه بدقة]

                📊 <b>تحليل الجودة الفنية:</b>
                - <b>الفينيسيون:</b> [تقييم دقيق من الصورة]
                - <b>الحالة العامة:</b> [بناء على النص]

                🎯 <b>رأي الخبير:</b> [لماذا تعتبر هذه همزة أو فخ؟]
                ✅ <b>المميزات:</b> 
                ❌ <b>العيوب:</b> 

                🔗 <b>الرابط:</b> {deal['link']}
                """

                # التحليل البصري (Types validation fix)
                image_bytes = requests.get(main_img).content
                contents = [
                    types.Part.from_text(text=elite_prompt),
                    types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg')
                ]

                # نظام الـ Retry لتجاوز أخطاء الشبكة
                response = client.models.generate_content(model=CONFIG["MODEL_ID"], contents=contents)
                
                # الإرسال لتيليغرام (نظام HTML)
                self.send_to_telegram(response.text, main_img)
                
                # حفظ ف الذاكرة لعدم التكرار
                self.save_id(deal['id'])
                
                self.log(f"✅ تم الإرسال. انتظار {CONFIG['WAIT_BETWEEN_DEALS']} ثانية...")
                time.sleep(CONFIG["WAIT_BETWEEN_DEALS"])

            except Exception as e:
                self.log(f"خطأ فـ التحليل: {e}", "ERROR")

    def send_to_telegram(self, report, img_url):
        url = f"https://api.telegram.org/bot{CONFIG['TELEGRAM_TOKEN']}/sendPhoto"
        safe_report = html.escape(report).replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')
        if len(safe_report) > 1000: safe_report = safe_report[:1000] + "..."
        payload = {"chat_id": CONFIG["TELEGRAM_CHAT_ID"], "photo": img_url, "caption": safe_report, "parse_mode": "HTML"}
        requests.post(url, json=payload, timeout=15)

    def run(self):
        try:
            self.init_session()
            self.hunt_listings()
            self.analyze_and_broadcast()
        finally:
            if self.driver: self.driver.quit()
            self.log("نهاية المهمة الإمبراطورية.")

if __name__ == "__main__":
    GrandmasterScout().run()