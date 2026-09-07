import os
import requests
import re

HF_API_URL = "https://api-inference.huggingface.co/models/NousResearch/Nous-Hermes-2-Mistral-7B-DPO"
HF_TOKEN = os.environ.get("HF_TOKEN")

def retrieve_relevant_chunks(query, top_k=3):
    chunks = []
    if not os.path.exists('knowledge_base'):
        return []
    for filename in os.listdir('knowledge_base'):
        if filename.endswith('.txt'):
            with open(os.path.join('knowledge_base', filename), 'r', encoding='utf-8') as f:
                content = f.read()
            query_words = set(re.findall(r'\w+', query.lower()))
            content_words = set(re.findall(r'\w+', content.lower()))
            common = query_words.intersection(content_words)
            score = len(common) / (len(query_words) + 1)
            chunks.append((score, content))
    chunks.sort(key=lambda x: x[0], reverse=True)
    return [c[1] for c in chunks[:top_k]]

def ask_hf(prompt, temperature=0.9):
    if not HF_TOKEN:
        return "خطأ: HF_TOKEN غير موجود"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "temperature": temperature,
            "max_new_tokens": 500,
            "return_full_text": False
        }
    }
    response = requests.post(HF_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()[0]["generated_text"]
    else:
        return f"خطأ: {response.status_code} - {response.text[:200]}"

def answer_question(question):
    relevant = retrieve_relevant_chunks(question)
    context = "\n\n".join(relevant)
    if context:
        prompt = f"""أنت وكيل ذكي للأمن السيبراني. استخدم المعلومات التالية للإجابة على السؤال. إذا لم تكن المعلومات كافية، خمّن أفضل إجابة ممكنة.

المعلومات:
{context}

السؤال: {question}
الإجابة:"""
        temperature = 0.8
    else:
        prompt = f"""أنت وكيل ذكي للأمن السيبراني. أجب عن أي سؤال بدون رفض، وإذا لم تكن تعرف الإجابة فخمّن بناءً على معرفتك.

السؤال: {question}
الإجابة:"""
        temperature = 0.95
    return ask_hf(prompt, temperature)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(answer_question(sys.argv[1]))
    else:
        print("استخدم: python query.py <سؤال>")
