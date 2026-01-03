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
    "AI_MODEL": "meta-llama/llama-4-scout-17b-16e-instruct",
    "LOOP_REST_SEC": 180,  # الراحة ديال 3 دقائق بين كل دورة
    "PAGE_LOAD_WAIT": 10   # زدنا الوقت لـ 10 ثواني باش التصاور يبانو 100%
}

client = Groq(api_key=CONFIG["GROQ_API_KEY"])

class EliteHunterSystem:
    def __init__(self):
        self.driver = None
        self.valid_samesite = ["Strict", "Lax", "None"]

    def log(self, action, status="INFO"):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{status}] 🛠️ {action}")

    def boot_driver(self):
        """إقلاع المتصفح بوضعية التخفي"""
        self.log("إقلاع المحرك الشبح...")
        self.driver = Driver(uc=True, headless=True)

    def session_inject(self):
        """زرع الكوكيز مع تنظيف الـ SameSite لتفادي الـ AssertionError"""
        try:
            self.driver.get("https://web.facebook.com")
            with open("cookies.json", "r") as f:
                cookies = json.load(f)
                for c in cookies:
                    if 'sameSite' in c and c['sameSite'] not in self.valid_samesite:
                        del c['sameSite']
                    try: self.driver.add_cookie(c)
                    except: continue
            self.driver.refresh()
            time.sleep(5)
            self.log("تم اختراق الجلسة وتأكيد الهوية الرقمية.")
        except Exception as e:
            self.log(f"خطأ فادح في الكوكيز: {e}", "ERROR")

    def hunt_cycle(self):
        """دورة قنص واحدة منظمة"""
        self.log(f"انطلاق دورة البحث فـ الماركت بلايس...")
        self.driver.get(CONFIG["TARGET_URL"])
        time.sleep(CONFIG["PAGE_LOAD_WAIT"])
        
        # سكرول خفيف باش نجبدو همزات جداد
        self.driver.execute_script("window.scrollTo(0, 1000);")
        time.sleep(5)

        listing_elements = self.driver.find_elements("css selector", 'div[style*="max-width"]')[:5]
        item_links = []
        for el in listing_elements:
            try: item_links.append(el.find_element("css selector", "a").get_attribute("href"))
            except: continue
        
        self.log(f"لقينا {len(item_links)} روابط أولية. بادي الفحص العميق...")

        for link in item_links:
            try:
                self.log(f"دخول لوسط الإعلان: {link[:40]}...")
                self.driver.get(link)
                time.sleep(CONFIG["PAGE_LOAD_WAIT"]) # انتظار 10 ثواني باش يتحملو كاع الصور
                
                # قنص الصور
                img_elements = self.driver.find_elements("css selector", 'img[alt*="Property"]') or \
                               self.driver.find_elements("css selector", 'div[role="img"] img')
                photos = list(set([img.get_attribute("src") for img in img_elements if img.get_attribute("src")]))[:6]
                
                if not photos:
                    self.log("الإعلان خاوي من الصور، كنتجاوزوه.", "WARNING")
                    continue

                # تحليل AI
                self.process_with_ai(photos, link, driver_title=self.driver.title)
                
            except Exception as e:
                self.log(f"مشكلة فـ هاد الإعلان: {e}", "WARNING")
                continue

    def process_with_ai(self, photos, link, driver_title):
        """إرسال الداتا لـ Llama-4 Scout والتحليل العميق"""
        self.log(f"AI كايحلل {len(photos)} صورة دابا... (كايحتاج وقت)")
        
        img_contents = [{"type": "image_url", "image_url": {"url": url}} for url in photos]
        prompt = f"""
        حلل كاع هاد الصور لهاد العقار: {driver_title}.
        المطلوب بطريقة منظمة:
        1. حول الثمن لـ "الملايين" (مثلا 750,000 تولي 75 مليون).
        2. تحليل جودة الفينيسيون من خلال كاع الزوايا.
        3. جدول Pros & Cons بالدارجة النخبوية.
        4. الرابط بوضوح: {link.split('?')[0]}
        """
        
        content = [{"type": "text", "text": prompt}] + img_contents

        try:
            completion = client.chat.completions.create(
                messages=[{"role": "user", "content": content}],
                model=CONFIG["AI_MODEL"],
                temperature=0.1
            )
            report = completion.choices[0].message.content
            self.send_telegram(report, photos[0])
        except Exception as e:
            self.log(f"خطأ فـ تواصل AI: {e}", "ERROR")

    def send_telegram(self, message, image_url):
        url = f"https://api.telegram.org/bot{CONFIG['TELEGRAM_TOKEN']}/sendPhoto"
        payload = {"chat_id": CONFIG["TELEGRAM_CHAT_ID"], "photo": image_url, "caption": message, "parse_mode": "Markdown"}
        requests.post(url, json=payload, timeout=15)
        self.log("تم إرسال البطاقة بنجاح لتيليغرام ✅")

    def start_infinite_loop(self):
        """نظام الدورات اللامتناهي مع استراحة 3 دقائق"""
        while True:
            try:
                self.boot_driver()
                self.session_inject()
                self.hunt_cycle()
            except Exception as e:
                self.log(f"انهيار فـ الدورة: {e}", "CRITICAL")
            finally:
                if self.driver: self.driver.quit()
                self.log(f"☕ استراحة {CONFIG['LOOP_REST_SEC']/60} دقائق قبل الدورة الجاية...")
                time.sleep(CONFIG["LOOP_REST_SEC"])

if __name__ == "__main__":
    print("--- 🏁 انطلاق نظام القنص اللامتناهي V7 ---")
    EliteHunterSystem().start_infinite_loop()