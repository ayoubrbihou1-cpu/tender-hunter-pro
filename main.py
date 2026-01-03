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
    "AI_MODEL": "meta-llama/llama-4-scout-17b-16e-instruct" # الموديل القناص
}

client = Groq(api_key=CONFIG["GROQ_API_KEY"])

def send_to_telegram(message, cover_image):
    """إرسال التقرير النهائي ببطاقة احترافية"""
    url = f"https://api.telegram.org/bot{CONFIG['TELEGRAM_TOKEN']}/sendPhoto"
    payload = {
        "chat_id": CONFIG["TELEGRAM_CHAT_ID"],
        "photo": cover_image,
        "caption": message,
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(url, json=payload, timeout=15)
        print(f"📡 Telegram Response: {r.status_code}")
    except Exception as e:
        print(f"⚠️ خطأ فـ إرسال تيليغرام: {e}")

def get_detailed_deals():
    """محرك القنص: كيدخل لوسط كل إعلان ويجمع كاع التصاور"""
    driver = Driver(uc=True, headless=True)
    structured_deals = []
    valid_samesite = ["Strict", "Lax", "None"]
    
    try:
        # 1. زرع الكوكيز مع تنظيف SameSite لتجنب AssertionError
        driver.get("https://web.facebook.com")
        with open("cookies.json", "r") as f:
            cookies = json.load(f)
            for c in cookies:
                if 'sameSite' in c and c['sameSite'] not in valid_samesite:
                    del c['sameSite']
                try:
                    driver.add_cookie(c)
                except: continue
        
        driver.refresh()
        print("🕵️‍♂️ انطلاق القنص العميق...")
        driver.get(CONFIG["TARGET_URL"])
        time.sleep(12)
        
        # كنجبدو روابط أول 4 ديال الإعلانات (لضمان السرعة والدقة)
        listing_elements = driver.find_elements("css selector", 'div[style*="max-width"]')[:4]
        print(f"🔍 لقينا {len(listing_elements)} إعلان أولي فـ الماركت بلايس.")
        
        item_links = []
        for el in listing_elements:
            try:
                link = el.find_element("css selector", "a").get_attribute("href")
                item_links.append(link)
            except: continue

        for link in item_links:
            try:
                print(f"🏠 كنفحصو العقار: {link[:50]}...")
                driver.get(link)
                time.sleep(6)
                
                # قنص كاع الصور (Multi-Image)
                img_elements = driver.find_elements("css selector", 'img[alt*="Property"]') or \
                               driver.find_elements("css selector", 'div[role="img"] img')
                
                all_photos = list(set([img.get_attribute("src") for img in img_elements if img.get_attribute("src")]))
                
                # استخراج النصوص (العنوان والثمن)
                title = driver.title.split('|')[0].strip()
                price_box = driver.find_elements("css selector", 'span[style*="-webkit-line-clamp"]')
                price_text = price_box[0].text if price_box else "غير محدد"
                
                if all_photos:
                    structured_deals.append({
                        "title": title,
                        "price": price_text,
                        "photos": all_photos[:6], # كنعطيو لـ AI أول 6 تصاور
                        "cover": all_photos[0],
                        "link": link.split('?')[0]
                    })
                    print(f"✅ تم جمع {len(all_photos)} صورة لهذا الإعلان.")
            except Exception as e:
                print(f"⚠️ فشل قنص تفاصيل الإعلان: {e}")
                continue
                
        return structured_deals
    finally:
        driver.quit()

def analyze_with_ai(deal):
    """تحليل شامل للصور والمعطيات بـ Llama-4 Scout"""
    print(f"🧠 AI كايحلل {len(deal['photos'])} تصويرة لـ {deal['title'][:20]}...")
    
    # بناء محتوى الرسالة لـ Groq Vision
    image_contents = [{"type": "image_url", "image_url": {"url": url}} for url in deal['photos']]
    
    prompt_text = f"""
    أنت مستشار عقاري نخبوي. حلل كاع هاد الصور لهاد العقار المغربي: {deal['title']}.
    الثمن المكتوب: {deal['price']}.
    
    المطلوب:
    1. حول الثمن لـ "الملايين" المغربية (مثلاً 1,200,000 DH تولي 120 مليون).
    2. استخرج رقم الهاتف إلا كان مكتوب فـ الإعلان.
    3. من خلال كاع التصاور، واش الفينيسيون مزيانة؟ (صالون، كوزينة، حمام).
    4. اكتب تقرير منظم بالدارجة النخبوية فيه: (🏠 العنوان، 💰 الثمن بالملايين، 🛠️ تقييم الفينيسيون، 📞 التواصل، 🔗 الرابط).
    """
    
    content = [{"type": "text", "text": prompt_text}] + image_contents

    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": content}],
            model=CONFIG["AI_MODEL"],
            temperature=0.1
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"❌ خطأ فـ AI: {e}")
        return None

if __name__ == "__main__":
    print("--- 🏁 انطلاق المهمة النخبوية ---")
    all_deals = get_detailed_deals()
    
    if not all_deals:
        print("🤷‍♂️ السيستيم مالقا حتى إعلان فـ هاد الدورة. جرب سكرول أكثر أو تأكد من الرابط.")
    
    for deal in all_deals:
        report = analyze_with_ai(deal)
        if report:
            send_to_telegram(report, deal['cover'])
            print(f"🚀 صيفطنا الهمزة: {deal['title'][:20]}")
            time.sleep(3) # راحة للـ API
            
    print("--- ✅ المهمة سالات بنجاح ---")