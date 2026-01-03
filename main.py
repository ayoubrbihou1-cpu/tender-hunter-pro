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

# --- بروتوكول الإعدادات العليا ---
CONFIG = {
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
    "TELEGRAM_TOKEN": os.getenv("TELEGRAM_TOKEN"),
    "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
    "TARGET_URL": "https://www.facebook.com/marketplace/fez/propertyrentals/?exact=false",
    "MODEL_ID": "gemini-2.5-flash", 
    "WAIT_BETWEEN_DEALS": 70 
}

client = genai.Client(api_key=CONFIG["GEMINI_API_KEY"])

class AtomicVisionHunter:
    def __init__(self):
        self.driver = None
        self.deals = []

    def log(self, msg, status="INFO"):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{status}] 🛡️ {msg}")

    def clean_fb_link(self, raw_link):
        """استخراج الـ Item ID الحقيقي لضمان عدم التوهان"""
        match = re.search(r'/item/(\d+)', raw_link)
        if match:
            return f"https://www.facebook.com/marketplace/item/{match.group(1)}/"
        return raw_link

    def init_session(self):
        self.log("إقلاع المحرك الجراحي (V17 - Atomic Sync)...")
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
        """قنص الداتا بنظام المزامنة الذرية لتفادي الخلط"""
        self.log(f"التوجه للهدف: {CONFIG['TARGET_URL']}")
        self.driver.get(CONFIG["TARGET_URL"])
        time.sleep(15)
        
        # سكرول ذكي لضمان تحميل الصور الصحيحة
        self.driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(5)
        
        cards = self.driver.find_elements("css selector", 'div[style*="max-width"]')[:4]
        self.log(f"تم رصد {len(cards)} بطاقات أولية. بادي القنص الجراحي...")

        for card in cards:
            try:
                # سكرول لكل كارد قبل استخراج الداتا لضمان المزامنة
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
                time.sleep(2)

                # استخراج الداتا من داخل نفس الحاوية (Atomic Extraction)
                img_elem = card.find_element("css selector", "img")
                img_url = img_elem.get_attribute("src")
                
                link_elem = card.find_element("css selector", "a")
                raw_link = link_elem.get_attribute("href")
                clean_link = self.clean_fb_link(raw_link)
                
                raw_text = card.text.split('\n')
                
                if "/marketplace/item/" in clean_link and len(raw_text) >= 2:
                    self.deals.append({
                        "price": raw_text[0], 
                        "title": raw_text[1], 
                        "link": clean_link, 
                        "image": img_url
                    })
                    self.log(f"✅ تم قنص: {raw_text[1][:20]}")
            except: continue

    def send_to_telegram(self, report, image_url):
        url = f"https://api.telegram.org/bot{CONFIG['TELEGRAM_TOKEN']}/sendPhoto"
        safe_report = html.escape(report).replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')
        
        if len(safe_report) > 1000:
            safe_report = safe_report[:1000] + "..."

        payload = {
            "chat_id": CONFIG["TELEGRAM_CHAT_ID"],
            "photo": image_url,
            "caption": safe_report,
            "parse_mode": "HTML"
        }
        try:
            res = requests.post(url, json=payload, timeout=15)
            if res.status_code != 200:
                self.log(f"❌ خطأ تيليغرام: {res.text}", "ERROR")
        except Exception as e:
            self.log(f"خطأ تقني: {e}", "ERROR")

    def analyze_and_broadcast(self):
        """تحليل نخبوي يربط بين الصورة والرابط بدقة"""
        for i, deal in enumerate(self.deals):
            self.log(f"تحليل الهمزة {i+1}/{len(self.deals)} بالرؤية الحاسوبية...")
            
            # برومبت يفرض على AI مطابقة الصورة مع المعلومات
            elite_prompt = f"""
            أنت خبير ومحلل عقاري نخبوي في المغرب. حلل هذا العقار بالدارجة المغربية بتركيز جراحي.
            
            المعطيات: {json.dumps(deal, ensure_ascii=False)}

            المطلوب تقرير نخبوي (أقل من 900 حرف):
            💎 <b>[اسم العقار من النص]</b>
            💰 <b>الثمن بالملايين:</b> [حول الثمن بدقة]
            📍 <b>الموقع:</b> [الموقع]

            📊 <b>تحليل النخبة:</b> [صف بدقة ما تراه في الصورة وهل يطابق النص؟]

            ✅ <b>المميزات:</b> (من الصورة والنص)
            ❌ <b>العيوب:</b> (من الصورة والنص)

            🔗 <b>الرابط المباشر:</b> {deal['link']}
            """

            try:
                # التأكد من تحميل الصورة الصحيحة
                image_resp = requests.get(deal['image'], timeout=10)
                image_bytes = image_resp.content

                contents = [
                    types.Part.from_text(text=elite_prompt),
                    types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg')
                ]

                response = client.models.generate_content(
                    model=CONFIG["MODEL_ID"],
                    contents=contents
                )
                
                report = response.text
                self.send_to_telegram(report, deal['image'])
                time.sleep(CONFIG["WAIT_BETWEEN_DEALS"])
            except Exception as e:
                self.log(f"خطأ فـ Gemini: {e}", "ERROR")

    def run(self):
        try:
            self.init_session()
            self.hunt_listings()
            self.analyze_and_broadcast()
        finally:
            if self.driver: self.driver.quit()

if __name__ == "__main__":
    AtomicVisionHunter().run()