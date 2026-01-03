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

def send_to_telegram(message, cover_image):
    """إرسال التقرير النهائي مع صورة الكوفر فقط للحفاظ على النقاء"""
    url = f"https://api.telegram.org/bot{CONFIG['TELEGRAM_TOKEN']}/sendPhoto"
    payload = {
        "chat_id": CONFIG["TELEGRAM_CHAT_ID"],
        "photo": cover_image,
        "caption": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=15)
    except Exception as e:
        print(f"⚠️ خطأ فني فـ تيليغرام: {e}")

def get_detailed_deals():
    """محرك القنص العميق: كيدخل لوسط كل إعلان ويجبد كاع التصاور"""
    driver = Driver(uc=True, headless=True)
    structured_deals = []
    
    try:
        # زرع الهوية الرقمية
        driver.get("https://web.facebook.com")
        with open("cookies.json", "r") as f:
            for c in json.load(f): driver.add_cookie(c)
        driver.refresh()
        
        print("🕵️‍♂️ بادي عملية القنص العميق...")
        driver.get(CONFIG["TARGET_URL"])
        time.sleep(random.uniform(10, 15))
        
        # كنجبدو أول 5 ديال "الهوتات" باش AI يركز مزيان
        listing_elements = driver.find_elements("css selector", 'div[style*="max-width"]')[:5]
        item_links = [el.find_element("css selector", "a").get_attribute("href") for el in listing_elements]

        for link in item_links:
            try:
                driver.get(link)
                time.sleep(5)
                
                # قنص كاع روابط التصاور فـ الإعلان
                img_elements = driver.find_elements("css selector", 'img[alt*="Property"]') or \
                               driver.find_elements("css selector", 'div[role="img"] img')
                
                all_photos = list(set([img.get_attribute("src") for img in img_elements if img.get_attribute("src")]))
                
                # استخراج النصوص
                title = driver.title.split('|')[0].strip()
                price_text = driver.find_element("css selector", 'span[style*="-webkit-line-clamp"]').text if driver.find_elements("css selector", 'span[style*="-webkit-line-clamp"]') else "غير محدد"
                
                structured_deals.append({
                    "title": title,
                    "price": price_text,
                    "photos": all_photos[:8], # كنصيفطو أول 8 تصاور لـ AI للتحليل
                    "cover": all_photos[0] if all_photos else None,
                    "link": link.split('?')[0]
                })
                print(f"✅ تم جمع {len(all_photos)} صورة لـ: {title[:20]}")
            except Exception as e:
                print(f"⚠️ تجاوزنا إعلان بسباب خطأ: {e}")
                continue
                
        return structured_deals
    finally:
        driver.quit()

def analyze_with_multi_vision(deal):
    """إرسال "باكاج" الصور لـ AI لتحليل الفينيسيون والحالة العامة"""
    # تحضير الصور لـ Groq Vision
    image_contents = [{"type": "image_url", "image_url": {"url": url}} for url in deal['photos']]
    
    prompt_content = [
        {
            "type": "text",
            "text": f"""
            Analyze ALL these images of this property: {deal['title']}.
            Price stated: {deal['price']}.
            
            Task:
            1. Look at the kitchen, bathrooms, and floors across all photos.
            2. Judge the 'Finition' quality (High/Medium/Low).
            3. Convert price to Moroccan 'Million' (e.g., 950,000 DH -> 95 مليون).
            4. Write a professional report in Moroccan Business Darija.
            
            Structure:
            💎 **[Title]**
            💰 **الثمن بالملايين:** [Price]
            🛠️ **حالة الفينيسيون:** [Based on all photos]
            ✅ **المميزات:**
            ❌ **العيوب المخفية:** (اللي بانت ليك فالتصاور)
            🔗 **الرابط:** {deal['link']}
            """
        }
    ] + image_contents

    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt_content}],
            model=CONFIG["AI_MODEL"],
            temperature=0.1
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"❌ AI تعذر عليه التحليل: {e}"

if __name__ == "__main__":
    print("🚀 الماكينة 'متعددة الأعين' انطلقت...")
    deals = get_detailed_deals()
    for d in deals:
        if d['photos']:
            report = analyze_with_multi_vision(d)
            send_to_telegram(report, d['cover'])
            print(f"🚀 صيفطنا التقرير لـ {d['title'][:20]}")
            time.sleep(5)
    print("✅ المهمة سالات بنجاح نخبوي.")