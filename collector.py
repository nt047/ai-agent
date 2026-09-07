import os
import requests
import feedparser
import json
import hashlib
from bs4 import BeautifulSoup
import re

RSS_FEEDS = [
    "https://krebsonsecurity.com/feed/",
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.bleepingcomputer.com/feed/",
    "https://www.schneier.com/blog/atom.xml",
    "https://www.reddit.com/r/netsec/.rss",
    "https://www.reddit.com/r/cybersecurity/.rss",
]

CVE_API = "https://cve.circl.lu/api/last"

def clean_text(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    for script in soup(["script", "style"]):
        script.decompose()
    text = soup.get_text(separator='\n')
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def save_chunk(text, source):
    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    if not os.path.exists('knowledge_base'):
        os.makedirs('knowledge_base')
    saved = []
    for chunk in chunks:
        h = hashlib.md5(chunk.encode()).hexdigest()[:8]
        filename = f"knowledge_base/{h}.txt"
        if not os.path.exists(filename):
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"المصدر: {source}\n\n{chunk}")
            saved.append(filename)
    return saved

def collect_from_rss():
    saved_total = []
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:5]:
                title = entry.get('title', 'بدون عنوان')
                link = entry.get('link', '')
                summary = entry.get('summary', '')
                full_text = f"{title}\n{summary}"
                if link:
                    try:
                        r = requests.get(link, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
                        full_text += "\n" + clean_text(r.text)[:2000]
                    except:
                        pass
                saved = save_chunk(full_text, link or feed_url)
                saved_total.extend(saved)
        except Exception as e:
            print(f"خطأ في {feed_url}: {e}")
    return saved_total

def collect_from_cve():
    saved_total = []
    try:
        r = requests.get(CVE_API, timeout=10)
        data = r.json()
        for item in data[:20]:
            cve_id = item.get('id', '')
            summary = item.get('summary', '')
            text = f"CVE: {cve_id}\n{summary}"
            saved = save_chunk(text, "CVE Database")
            saved_total.extend(saved)
    except Exception as e:
        print(f"خطأ في CVE: {e}")
    return saved_total

def main():
    print("بدء جمع المعلومات...")
    saved = []
    saved.extend(collect_from_rss())
    saved.extend(collect_from_cve())
    print(f"تم حفظ {len(saved)} جزءًا جديدًا")
    with open('last_run.txt', 'w') as f:
        f.write(f"تم التشغيل وحفظ {len(saved)} جزءًا")

if __name__ == "__main__":
    main()
