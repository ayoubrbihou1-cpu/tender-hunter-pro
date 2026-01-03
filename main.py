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

class DeepScoutHunter:
    def __init__(self):
        self.driver = None
        self.deals = []
        self.processed_ids = set()

    def log(self, msg, status="INFO"):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{status}] 🛡️ {msg}")

    def clean_fb_link(self, raw_link):
        match = re.search(r'/item/(\d+)', raw_link)
        if match:
            return match.group(1), f"https://www.facebook.com/marketplace/item/{match.group(1)}/"
        return None, raw_link

    def init_session(self):
        self.log("إقلاع المحرك الجراحي العميق (V18.1 - Fixed)...")
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
            self.log("تم تأكيد الهوية الرقمية.")
        except Exception as e:
            self.log(f"فشل الجلسة: {e}", "CRITICAL")
            raise

    def hunt_listings(self):
        self.log(f"التوجه للهدف: {CONFIG['TARGET_URL']}")
        self.driver.get(CONFIG["TARGET_URL"])
        time.sleep(15)
        self.driver.execute_script("window.scrollTo(0, 1000);")
        time.sleep(5)
        
        cards = self.driver.find_elements("css selector", 'div[style*="max-width"]')[:4]
        for card in cards:
            try:
                link_elem = card.find_element("css selector", "a")
                item_id, clean_link = self.clean_fb_link(link_elem.get_attribute("href"))
                
                if item_id and item_id not in self.processed_ids:
                    self.deals.append({"id": item_id, "link": clean_link})
                    self.processed_ids.add(item_id)
            except: continue
        self.log(f"تم حجز {len(self.deals)} روابط للفحص.")

    def analyze_and_broadcast(self):
        for i, deal in enumerate(self.deals):
            try:
                self.log(f"اختراق الإعلان {i+1}: {deal['link']}")
                self.driver.get(deal['link'])
                time.sleep(10)

                # --- تصحيح عصب الخطأ: استخراج الصورة بنظام الفلترة (Robust Selection) ---
                try:
                    # كنقلبو على أول صورة كبيرة ف الصفحة ماشي ب الـ alt
                    main_img_elem = self.driver.find_element("css selector", "div[role='main'] img[src*='fbcdn']")
                    main_img = main_img_elem.get_attribute("src")
                except:
                    self.log("⚠️ فشل Selector الصورة الأول، كنحاول البديل...", "WARNING")
                    main_img = self.driver.find_element("css selector", "img[cursor='pointer']").get_attribute("src")

                # فتح الـ Description كاملة
                try:
                    see_more = self.driver.find_element("xpath", "//span[contains(text(), 'Voir plus') or contains(text(), 'See more')]")
                    self.driver.execute_script("arguments[0].click();", see_more)
                    time.sleep(2)
                except: pass

                full_desc = self.driver.find_element("css selector", "div[dir='auto']").text
                
                elite_prompt = f"""
                أنت 'المرشد الأعظم' خبير العقارات في المغرب. حلل هذا الإعلان بعمق بالدارجة المغربية:
                الوصف: {full_desc}
                الرابط: {deal['link']}

                المطلوب:
                💎 <b>[عنوان ذكي]</b>
                💰 <b>الثمن بالملايين:</b>
                📍 <b>الموقع:</b>
                📞 <b>الهاتف:</b> [استخرجه بدقة من النص]
                📊 <b>تحليل جودة الفينيسيون (الأرضية، المطبخ، الحمام):</b>
                🎯 <b>رأي الخبير:</b> [هل هو أفضل اقتراح؟]
                ✅ <b>المميزات:</b>
                ❌ <b>العيوب:</b>
                🔗 <b>الرابط:</b> {deal['link']}
                """

                # التحليل البصري
                image_bytes = requests.get(main_img).content
                contents = [
                    types.Part.from_text(text=elite_prompt),
                    types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg')
                ]

                response = client.models.generate_content(model=CONFIG["MODEL_ID"], contents=contents)
                self.send_to_telegram(response.text, main_img)
                time.sleep(CONFIG["WAIT_BETWEEN_DEALS"])

            except Exception as e:
                self.log(f"فشل فـ تحليل الإعلان {i+1}: {e}", "ERROR")

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

if __name__ == "__main__":
    DeepScoutHunter().run()