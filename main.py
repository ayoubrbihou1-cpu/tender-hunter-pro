import os
import time
import json
import requests
import html 
from google import genai
from google.genai import types # ضروري للتعامل مع الصور بلا ValidationError
from seleniumbase import Driver
from datetime import datetime

# --- بروتوكول الإعدادات النخبوية ---
CONFIG = {
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
    "TELEGRAM_TOKEN": os.getenv("TELEGRAM_TOKEN"),
    "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
    "TARGET_URL": "https://www.facebook.com/marketplace/fez/propertyrentals/?exact=false",
    "MODEL_ID": "gemini-2.5-flash", # المحرك المعتمد فـ 2026
    "WAIT_BETWEEN_DEALS": 70 # زيادة الأمان لتفادي Resource Exhausted
}

client = genai.Client(api_key=CONFIG["GEMINI_API_KEY"])

class UltimateVisionHunter:
    def __init__(self):
        self.driver = None
        self.deals = []

    def log(self, msg, status="INFO"):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{status}] 🛡️ {msg}")

    def init_session(self):
        self.log("إقلاع المحرك الفولاذي (V16 - Vision Pro)...")
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
            self.log("تم تأكيد الهوية الرقمية.")
        except Exception as e:
            self.log(f"فشل الجلسة: {e}", "CRITICAL")
            raise

    def hunt_listings(self):
        self.log(f"التوجه للهدف: {CONFIG['TARGET_URL']}")
        self.driver.get(CONFIG["TARGET_URL"])
        time.sleep(15)
        self.driver.execute_script("window.scrollTo(0, 800);")
        time.sleep(5)
        cards = self.driver.find_elements("css selector", 'div[style*="max-width"]')[:3]
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
        self.log(f"تم قنص {len(self.deals)} بطاقات.")

    def send_to_telegram(self, report, image_url):
        url = f"https://api.telegram.org/bot{CONFIG['TELEGRAM_TOKEN']}/sendPhoto"
        # تنظيف HTML لضمان وصول الميساج بحال "تححححح.PNG"
        safe_report = html.escape(report).replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')
        
        payload = {
            "chat_id": CONFIG["TELEGRAM_CHAT_ID"],
            "photo": image_url,
            "caption": safe_report,
            "parse_mode": "HTML"
        }
        try:
            res = requests.post(url, json=payload, timeout=15)
            if res.status_code == 200:
                self.log("✅ تم الإرسال بنجاح.")
            else:
                self.log(f"❌ خطأ تيليغرام: {res.text}", "ERROR")
        except Exception as e:
            self.log(f"خطأ تقني: {e}", "ERROR")

    def analyze_and_broadcast(self):
        """التحليل النخبوي البصري (Vision) لتفادي ValidationError"""
        for i, deal in enumerate(self.deals):
            self.log(f"تحليل الهمزة {i+1}/{len(self.deals)} بالرؤية الحاسوبية...")
            
            # برومبت نخبوي شامل (ستايل تححححح.PNG)
            elite_prompt = f"""
            أنت خبير ومحلل عقاري نخبوي في المغرب. حلل هذا العقار بالدارجة المغربية بناءً على الصورة والنص.
            
            المعطيات من النص: {json.dumps(deal, ensure_ascii=False)}

            المطلوب تقرير منظم كالتالي:
            💎 <b>[اسم العقار]</b>
            💰 <b>الثمن بالملايين:</b> [حول الثمن لمليون مغربي بدقة]
            📍 <b>الموقع:</b> [استخرج الموقع]

            📊 <b>تحليل النخبة:</b> [حلل الفينيسيون، الحالة، وهل السعر مناسب لما يظهر في الصورة؟]

            ✅ <b>المميزات:</b>
            - [من الصورة]
            - [من النص]

            ❌ <b>العيوب:</b>
            - [شيء سلبي تلاحظه]

            📞 <b>للتواصل:</b> Contact via link
            🔗 <b>الرابط:</b> {deal['link']}
            
            استعمل فقط وسم <b> و </b> للتغليظ.
            """

            try:
                # تحميل الصورة كـ Bytes لتفادي ValidationError
                image_resp = requests.get(deal['image'])
                image_bytes = image_resp.content

                # بناء الـ Contents بالطريقة الصحيحة للـ SDK الجديد
                contents = [
                    types.Part.from_text(text=elite_prompt),
                    types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg')
                ]

                # الاستدعاء النخبوي
                response = client.models.generate_content(
                    model=CONFIG["MODEL_ID"],
                    contents=contents
                )
                
                report = response.text
                self.send_to_telegram(report, deal['image'])
                
                # راحة تقنية لحماية الكوطا
                time.sleep(CONFIG["WAIT_BETWEEN_DEALS"])
            except Exception as e:
                self.log(f"خطأ فـ Gemini Vision: {e}", "ERROR")

    def run(self):
        try:
            self.init_session()
            self.hunt_listings()
            self.analyze_and_broadcast()
        finally:
            if self.driver: self.driver.quit()

if __name__ == "__main__":
    UltimateVisionHunter().run()