import os
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

class EliteBulletproofHunter:
    def __init__(self):
        self.driver = None
        self.valid_samesite = ["Strict", "Lax", "None"]

    def log(self, action, status="DEBUG"):
        """نظام تتبع العمليات بالساعة والدقيقة"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{status}] 🛡️ {action}")

    def boot_and_inject(self):
        """إقلاع المحرك واختراق الجلسة بالكوكيز"""
        self.log("إقلاع المحرك الشبح...")
        self.driver = Driver(uc=True, headless=True)
        try:
            self.driver.get("https://web.facebook.com")
            # زرع الكوكيز مع التنظيف من شوائب sameSite
            with open("cookies.json", "r") as f:
                cookies = json.load(f)
                for c in cookies:
                    if 'sameSite' in c and c['sameSite'] not in self.valid_samesite:
                        del c['sameSite']
                    try:
                        self.driver.add_cookie(c)
                    except:
                        continue
            self.driver.refresh()
            time.sleep(5)
            self.driver.save_screenshot("debug_1_home.png")
            self.log("تم زرع الكوكيز بنجاح. سكرين شوت (1) واجدة.")
        except Exception as e:
            self.log(f"خطأ في الكوكيز: {e}", "ERROR")

    def run_safe_mission(self):
        """دورة قنص آمنة مبنية على المبادئ الأولى"""
        self.log(f"التوجه للهدف: {CONFIG['TARGET_URL']}")
        self.driver.get(CONFIG["TARGET_URL"])
        time.sleep(12)
        self.driver.save_screenshot("debug_2_marketplace.png")

        # الخطوة 1: فصل جمع البيانات عن المعالجة (Decoupling)
        # هاد السطر كيقتل مشكلة stale element reference نهائياً
        cards = self.driver.find_elements("css selector", 'div[style*="max-width"]')[:3]
        extracted_data = []

        for i, card in enumerate(cards):
            try:
                extracted_data.append({
                    "cover": card.find_element("css selector", "img").get_attribute("src"),
                    "link": card.find_element("css selector", "a").get_attribute("href"),
                    "title": card.text.split('\n')[1] if len(card.text.split('\n')) > 1 else "عقار مغربي"
                })
            except Exception as e:
                self.log(f"تجاوز عنصر أولي بسباب خطأ: {e}", "WARNING")

        self.log(f"تم تخزين {len(extracted_data)} روابط فـ الذاكرة. بادي الفحص العميق...")

        # الخطوة 2: المعالجة الفردية لكل رابط معزول
        for i, item in enumerate(extracted_data):
            try:
                self.log(f"فحص الهمزة {i+1}: {item['title'][:25]}")
                self.driver.get(item['link'])
                time.sleep(8)
                self.driver.save_screenshot(f"debug_3_item_{i+1}.png")

                # قنص الصور الداخلية بـ Selectors مرنة
                raw_imgs = self.driver.find_elements("css selector", 'img[src*="fbcdn"]')
                # فلترة الروابط (HTTP فقط وبلا تكرار) لتفادي Error 400
                clean_photos = []
                for img in raw_imgs:
                    src = img.get_attribute("src")
                    if src and src.startswith("http") and src not in clean_photos:
                        clean_photos.append(src)
                
                final_photos = clean_photos[:5] # نكتفي بـ 5 صور للجودة

                # Fallback: إلا مالقينا والو لداخل، كنخدمو بصورة الكوفر اللي خدينا فـ اللول
                if not final_photos and item['cover']:
                    final_photos = [item['cover']]

                if final_photos:
                    self.process_ai_and_notify(final_photos, item['link'], item['title'])
                
            except Exception as e:
                self.log(f"فشل في معالجة الإعلان {i+1}: {e}", "ERROR")

    def process_ai_and_notify(self, photos, link, title):
        """تحليل ذكي وإرسال التقرير لمركز القيادة"""
        self.log(f"AI كايحلل {len(photos)} صورة... (Llama-4 Scout)")
        
        # تنظيم الداتا لـ Groq Vision بلا غلط
        img_contents = [{"type": "image_url", "image_url": {"url": url}} for url in photos]
        
        prompt_text = f"""
        أنت مستشار عقاري مغربي نخبوي. حلل هاد العقار: {title}.
        المطلوب بالدارجة المغربية المجهدة:
        1. حول الثمن لـ "مليون" (مثلا 850,000 DH تولي 85 مليون).
        2. جدول Pros & Cons بوضوح.
        3. رأيك الشخصي واش هادي "همزة" ولا لا.
        4. الرابط بوضوح فـ النهاية: {link.split('?')[0]}
        """
        
        try:
            completion = client.chat.completions.create(
                messages=[{"role": "user", "content": [{"type": "text", "text": prompt_text}] + img_contents}],
                model=CONFIG["AI_MODEL"],
                temperature=0.1
            )
            report = completion.choices[0].message.content
            
            # الإرسال لتيليغرام مع أول صورة
            requests.post(f"https://api.telegram.org/bot{CONFIG['TELEGRAM_TOKEN']}/sendPhoto", 
                         json={"chat_id": CONFIG["TELEGRAM_CHAT_ID"], "photo": photos[0], "caption": report, "parse_mode": "Markdown"})
            self.log("✅ التقرير مشى لتيليغرام بنجاح.")
        except Exception as e:
            self.log(f"خطأ فـ AI: {e}", "ERROR")

    def execute_one_shot(self):
        """تشغيل دورة واحدة كاملة للتحقيق والتنفيذ"""
        try:
            self.boot_and_inject()
            self.run_safe_mission()
        finally:
            if self.driver:
                self.driver.quit()
                self.log("إغلاق المتصفح. انتهت المهمة.")

if __name__ == "__main__":
    print("--- 🏁 انطلاق نظام V8.3 الفولاذي ---")
    EliteBulletproofHunter().execute_one_shot()