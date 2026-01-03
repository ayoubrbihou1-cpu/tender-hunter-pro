import os, time, random, json, requests
from seleniumbase import Driver
from groq import Groq
from datetime import datetime

CONFIG = {
    "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
    "TELEGRAM_TOKEN": os.getenv("TELEGRAM_TOKEN"),
    "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
    "TARGET_URL": "https://web.facebook.com/marketplace/casablanca/propertyforsale",
    "AI_MODEL": "meta-llama/llama-4-scout-17b-16e-instruct"
}

client = Groq(api_key=CONFIG["GROQ_API_KEY"])

def send_to_telegram(message, cover_image):
    url = f"https://api.telegram.org/bot{CONFIG['TELEGRAM_TOKEN']}/sendPhoto"
    payload = {"chat_id": CONFIG["TELEGRAM_CHAT_ID"], "photo": cover_image, "caption": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload, timeout=15)

def get_detailed_deals():
    driver = Driver(uc=True, headless=True)
    structured_deals = []
    valid_samesite = ["Strict", "Lax", "None"]
    
    try:
        driver.get("https://web.facebook.com")
        with open("cookies.json", "r") as f:
            cookies = json.load(f)
            for c in cookies:
                # تنظيف الكوكي لتجنب AssertionError
                if 'sameSite' in c and c['sameSite'] not in valid_samesite:
                    del c['sameSite']
                try:
                    driver.add_cookie(c)
                except: continue
        
        driver.refresh()
        print("🕵️‍♂️ انطلاق القنص العميق المنظم...")
        driver.get(CONFIG["TARGET_URL"])
        time.sleep(12)
        
        listing_elements = driver.find_elements("css selector", 'div[style*="max-width"]')[:5]
        item_links = [el.find_element("css selector", "a").get_attribute("href") for el in listing_elements]

        for link in item_links:
            try:
                driver.get(link)
                time.sleep(5)
                img_elements = driver.find_elements("css selector", 'img[alt*="Property"]') or \
                               driver.find_elements("css selector", 'div[role="img"] img')
                all_photos = list(set([img.get_attribute("src") for img in img_elements if img.get_attribute("src")]))
                
                title = driver.title.split('|')[0].strip()
                # استخراج الثمن بدقة
                price_box = driver.find_elements("css selector", 'span[style*="-webkit-line-clamp"]')
                price_text = price_box[0].text if price_box else "غير محدد"
                
                structured_deals.append({
                    "title": title, "price": price_text, 
                    "photos": all_photos[:8], "cover": all_photos[0] if all_photos else None,
                    "link": link.split('?')[0]
                })
            except: continue
                
        return structured_deals
    finally:
        driver.quit()

def analyze_with_multi_vision(deal):
    image_contents = [{"type": "image_url", "image_url": {"url": url}} for url in deal['photos']]
    prompt_content = [{"type": "text", "text": f"حلل هاد الصور ديال عقار {deal['title']} بثمن {deal['price']}. حول الثمن للملايين المغربية، عطيني عيوب بانت ليك فالفينيسيون، ونظم التقرير بالدارجة النخبوية مع Pros & Cons بوضوح. الرابط: {deal['link']}"}] + image_contents
    
    completion = client.chat.completions.create(messages=[{"role": "user", "content": prompt_content}], model=CONFIG["AI_MODEL"], temperature=0.1)
    return completion.choices[0].message.content

if __name__ == "__main__":
    print("🚀 الماكينة 'متعددة الأعين' عادت للعمل...")
    deals = get_detailed_deals()
    for d in deals:
        if d['photos'] and d['cover']:
            report = analyze_with_multi_vision(d)
            send_to_telegram(report, d['cover'])
            time.sleep(5)
    print("✅ المهمة سالات بنجاح.")