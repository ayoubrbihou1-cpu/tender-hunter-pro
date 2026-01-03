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
    "AI_MODEL": "meta-llama/llama-4-scout-17b-16e-instruct"
}

client = Groq(api_key=CONFIG["GROQ_API_KEY"])

class OneShotDebugHunter:
    def __init__(self):
        self.driver = None
        self.valid_samesite = ["Strict", "Lax", "None"]

    def log(self, action, status="DEBUG"):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{status}] 🕵️ {action}")

    def boot_and_inject(self):
        """إقلاع المتصفح وزرع الكوكيز"""
        self.log("إقلاع المحرك...")
        self.driver = Driver(uc=True, headless=True) # خليه Headless حيت حنا فـ Codespace
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
            # سكرين شوت باش نتأكدوا باللي دخلنا لفيسبوك (Logged in)
            self.driver.save_screenshot("debug_1_facebook_home.png")
            self.log("تم زرع الكوكيز. سكرين شوت (1) واجدة.")
        except Exception as e:
            self.log(f"خطأ في الكوكيز: {e}", "ERROR")

    def run_debug_cycle(self):
        """دورة واحدة فقط للفحص الشامل"""
        self.log(f"الذهاب للماركت بلايس: {CONFIG['TARGET_URL']}")
        self.driver.get(CONFIG["TARGET_URL"])
        time.sleep(12)
        
        # سكرين شوت للماركت بلايس قبل أي حاجة
        self.driver.save_screenshot("debug_2_marketplace_main.png")
        self.log("وصلنا للماركت بلايس. سكرين شوت (2) واجدة.")

        cards = self.driver.find_elements("css selector", 'div[style*="max-width"]')[:3] # غانجربو فـ 3 فقط
        
        if not cards:
            self.log("❌ مالقينا حتى بطاقة إعلان! الصفحة خاوية أو الـ Selector تبدل.", "ERROR")
            return

        for i, card in enumerate(cards):
            try:
                cover_img = card.find_element("css selector", "img").get_attribute("src")
                link = card.find_element("css selector", "a").get_attribute("href")
                title = card.text.split('\n')[1] if len(card.text.split('\n')) > 1 else "عقار"

                self.log(f"دخول عميق للإعلان رقم {i+1}: {title[:20]}")
                self.driver.get(link)
                time.sleep(10) # انتظار طويل للتأكد من التحميل
                
                # سكرين شوت لوسط الإعلان
                self.driver.save_screenshot(f"debug_3_item_{i+1}_inside.png")
                
                # البحث عن الصور بجميع الطرق الممكنة
                all_photos = []
                selectors = ['img[src*="fbcdn"]', 'img[alt*="Property"]', 'div[role="img"] img']
                for selector in selectors:
                    found = self.driver.find_elements("css selector", selector)
                    all_photos.extend([img.get_attribute("src") for img in found if img.get_attribute("src")])
                
                final_photos = list(set([p for p in all_photos if p]))[:6]

                if not final_photos:
                    self.log(f"⚠️ الإعلان رقم {i+1} بان لينا خاوي لداخل. الصور ما بانوش.", "WARNING")
                    final_photos = [cover_img] if cover_img else []

                # تحليل AI وإرسال
                if final_photos:
                    self.process_with_ai(final_photos, link, title)
                
            except Exception as e:
                self.log(f"فشل في الإعلان {i+1}: {e}", "ERROR")

    def process_with_ai(self, photos, link, title):
        self.log(f"AI كايحلل {len(photos)} صورة...")
        img_contents = [{"type": "image_url", "image_url": {"url": url}} for url in photos if url]
        prompt = f"حلل هاد العقار ({title}) حول الثمن للملايين وعطيني Pros & Cons بالدارجة. الرابط: {link.split('?')[0]}"
        
        try:
            completion = client.chat.completions.create(
                messages=[{"role": "user", "content": [{"type": "text", "text": prompt}] + img_contents}],
                model=CONFIG["AI_MODEL"],
                temperature=0.1
            )
            report = completion.choices[0].message.content
            # إرسال لتيليغرام
            requests.post(f"https://api.telegram.org/bot{CONFIG['TELEGRAM_TOKEN']}/sendPhoto", 
                         json={"chat_id": CONFIG["TELEGRAM_CHAT_ID"], "photo": photos[0], "caption": report, "parse_mode": "Markdown"})
            self.log(f"✅ تم إرسال التقرير بنجاح لتيليغرام.")
        except Exception as e:
            self.log(f"خطأ AI: {e}", "ERROR")

    def execute(self):
        try:
            self.boot_and_inject()
            self.run_debug_cycle()
        finally:
            if self.driver:
                self.driver.quit()
                self.log("إغلاق المتصفح. انتهت الدورة الواحدة.")

if __name__ == "__main__":
    OneShotDebugHunter().execute()