import os
import requests
from bs4 import BeautifulSoup
import re
import hashlib

def extract_text_from_url(url):
    try:
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text(separator='\n')
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    except Exception as e:
        return f"خطأ: {e}"

def save_knowledge(text, source):
    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    if not os.path.exists('knowledge_base'):
        os.makedirs('knowledge_base')
    saved = []
    for chunk in chunks:
        h = hashlib.md5(chunk.encode()).hexdigest()[:8]
        filename = f"knowledge_base/{h}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"المصدر: {source}\n\n{chunk}")
        saved.append(filename)
    return saved

def learn_from_text(text, source="نص يدوي"):
    return save_knowledge(text, source)
