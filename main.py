import os
import time
import random
import requests
from seleniumbase import Driver
from groq import Groq

# إعداد المفاتيح
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CLIENT_NICHE = "الكهرباء والطاقة الشمسية"

client = Groq(api_key=GROQ_API_KEY)

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error sending to Telegram: {e}")

def get_tenders():
    driver = Driver(uc=True, headless=True)
    url = "https://www.marchespublics.gov.ma/pmws/index.py/appeloffredvpt"
    
    try:
        driver.uc_open_with_reconnect(url, reconnect_time=5)
        time.sleep(random.uniform(5, 10)) 
        
        items = driver.find_elements("css selector", "tr.back-color-white")
        tenders = []
        for item in items[:8]:
            title = item.find_element("css selector", "td.title").text.strip()
            link = item.find_element("css selector", "a").get_attribute("href")
            tenders.append({"title": title, "link": link})
        return tenders
    except Exception as e:
        print(f"Scraping Error: {e}")
    finally:
        driver.quit()

def analyze_and_notify(tenders):
    for t in tenders:
        prompt = f"Analyze this tender: '{t['title']}'. Industry: '{CLIENT_NICHE}'. If relevant, summarize in 2 lines of Moroccan Darija. Else return 'NO'."
        completion = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192")
        analysis = completion.choices[0].message.content
        
        if "NO" not in analysis.upper():
            msg = f"🔥 *فرصة جديدة:*\n{analysis}\n🔗 [الرابط]({t['link']})"
            send_telegram_msg(msg)

if __name__ == "__main__":
    print("🚀 الماكينة بدات...")
    data = get_tenders()
    if data:
        analyze_and_notify(data)
    print("✅ تم بنجاح.")