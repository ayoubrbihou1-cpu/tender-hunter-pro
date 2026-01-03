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
    "MAX_DEALS_PER_RUN": 2, 
    "WAIT_BETWEEN_DEALS": 90, # زدنا الوقت لـ 90 ثانية لضمان صفاء الكوطا
    "DB_FILE": "processed_deals.txt"
}

client = genai.Client(api_key=CONFIG["GEMINI_API_KEY"])

class GrandmasterPropertyScout:
    def __init__(self):
        self.driver = None
        self.deals = []
        self.processed_ids = self.load_processed_ids()

    def log(self, msg, status="INFO"):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{status}] 🛡️ {msg}")

    def load_processed_ids(self):
        if os.path.exists(CONFIG["DB_FILE"]):
            with open(CONFIG["DB_FILE"], "r") as f:
                return set(line.strip() for line in f)
        return set()

    def save_id(self, item_id):
        with open(CONFIG["DB_FILE"], "a") as f:
            f.write(f"{item_id}\n")
        self.processed_ids.add(item_id)

    def clean_fb_link(self, raw_link):
        match = re.search(r'/item/(\d+)', raw_link)
        if match:
            return match.group(1), f"https://www.facebook.com/marketplace/item/{match.group(1)}/"
        return None, raw_link

    def init_session(self):
        self.log("إقلاع المحرك الإمبراطوري V21.0...")
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
        self.log(f"التوجه للهدف: {CONFIG['TARGET_URL']}")
        self.driver.get(CONFIG["TARGET_URL"])
        time.sleep(15)
        self.driver.execute_script("window.scrollTo(0, 1000);")
        time.sleep(5)
        
        cards = self.driver.find_elements("css selector", 'div[style*="max-width"]')[:5]
        for card in cards:
            try:
                link_elem = card.find_element("css selector", "a")
                item_id, clean_link = self.clean_fb_link(link_elem.get_attribute("href"))
                if item_id and item_id not in self.processed_ids:
                    self.deals.append({"id": item_id, "link": clean_link})
                    if len(self.deals) >= CONFIG["MAX_DEALS_PER_RUN"]: break
            except: continue
        self.log(f"تم حجز {len(self.deals)} روابط جديدة.")

    def analyze_and_broadcast(self):
        """التحليل النخبوي مع نظام حماية الكوطا (Circuit Breaker)"""
        for i, deal in enumerate(self.deals):
            try:
                self.log(f"اختراق الإعلان {i+1}: {deal['link']}")
                self.driver.get(deal['link'])
                time.sleep(12)

                # استخراج الصورة والوصف
                try:
                    main_img = self.driver.find_element("css selector", "div[role='main'] img[src*='fbcdn']").get_attribute("src")
                except:
                    main_img = self.driver.find_element("css selector", "img[cursor='pointer']").get_attribute("src")

                try:
                    see_more = self.driver.find_element("xpath", "//span[contains(text(), 'Voir plus') or contains(text(), 'See more') or contains(text(), 'عرض المزيد')]")
                    self.driver.execute_script("arguments[0].click();", see_more)
                    time.sleep(2)
                except: pass

                desc_elements = self.driver.find_elements("css selector", "span[dir='auto'], div[dir='auto']")
                full_desc = " ".join([el.text for el in desc_elements if len(el.text) > 40])
                if not full_desc: full_desc = "الوصف غير متوفر."

                # برومبت نخبوي مختصر
                elite_prompt = f"""
                أنت خبير عقارات نخبوي. حلل هذا الإعلان باختصار شديد بالدارجة المغربية:
                {full_desc[:1200]}
                💎 [عنوان] | 💰 [ثمن] | 📍 [حي] | 📞 [هاتف]
                📊 [جودة الفينيسيون] | 🎯 [رأي الخبير]
                ✅ [ميزة] | ❌ [عيب] | 🔗 {deal['link']}
                """

                # التحليل البصري
                image_bytes = requests.get(main_img).content
                contents = [
                    types.Part.from_text(text=elite_prompt),
                    types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg')
                ]

                # طلب التحليل
                response = client.models.generate_content(model=CONFIG["MODEL_ID"], contents=contents)
                self.send_to_telegram(response.text, main_img)
                self.save_id(deal['id'])
                self.log(f"✅ تم الإرسال بنجاح.")

            except Exception as e:
                self.log(f"خطأ فـ التحليل: {e}", "ERROR")
                # --- نظام Circuit Breaker الجديد ---
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    self.log("🛑 حظر الكوطا! حبس الماكينة دابا باش ما نحرقوش الساروت.", "CRITICAL")
                    return # الخروج من الدالة كاملة فوراً

            finally:
                # الـ Sleep دابا إجباري وخا يوقع أي خطأ باش المتصفح يرتاح
                self.log(f"انتظار تقني {CONFIG['WAIT_BETWEEN_DEALS']} ثانية...")
                time.sleep(CONFIG["WAIT_BETWEEN_DEALS"])

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
    GrandmasterPropertyScout().run()