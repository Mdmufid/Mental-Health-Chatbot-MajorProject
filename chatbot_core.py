import os, json, re, requests
from collections import deque
from dotenv import load_dotenv
import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
MODEL_PATH = os.getenv("MODEL_PATH", "emotion_model/models/transformer_model_v3")  # ✅ updated to v3

if not OPENROUTER_API_KEY:
    raise ValueError("❌ No OpenRouter API key found in .env file")

# Load model
tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_PATH)
emo_model = DistilBertForSequenceClassification.from_pretrained(MODEL_PATH)
emo_model.eval()

# Label map
label_map_path = os.path.join(MODEL_PATH, "label_map.json")
if os.path.exists(label_map_path):
    with open(label_map_path, "r") as f:
        label_map = json.load(f)
    id_to_label = {int(v): k for k, v in label_map.items()}
else:
    id_to_label = {0: "anger", 1: "fear", 2: "joy", 3: "love", 4: "neutral", 5: "sadness"}

# Short-term conversation memory
conversation_memory = deque(maxlen=8)
emotion_memory = deque(maxlen=8)

def detect_emotion(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        logits = emo_model(**inputs).logits
        pred = int(torch.argmax(logits, dim=-1).cpu().numpy()[0])
    emotion = id_to_label.get(pred, "neutral")
    return emotion, emotion  # ✅ broad and fine are now the same

# Safety Filters
def is_crisis(text):
    t = text.lower()
    return bool(re.search(r"\b(suicide|kill myself|end my life|want to die|self harm)\b", t))

def is_explicit(text):
    t = text.lower()
    return bool(re.search(r"\b(horny|sex|porn|nude|fuck|dick|boobs)\b", t))

# OpenRouter LLM Response Generator
def generate_llm_reply(message, emotion, fine_emotion, context):
    system_prompt = (
        "You are an empathetic AI mental health companion. "
        "Provide emotional support, motivation, and practical self-care guidance. "
        "Avoid repetition and medical or explicit advice."
    )

    convo_context = "\n".join([f"User: {m['user']}\nBot: {m['bot']}" for m in context])

    user_prompt = (
        f"Recent conversation:\n{convo_context}\n\n"
        f"User message: {message}\n"
        f"Detected emotion: {emotion} ({fine_emotion})\n\n"
        f"Reply with empathy, 2–4 sentences, offering comfort and practical suggestions."
    )

    payload = {
        "model": "meta-llama/llama-3.1-70b-instruct",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.8,
        "max_tokens": 300
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "AI Mental Health Companion",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(f"{BASE_URL}/chat/completions", json=payload, headers=headers, timeout=30)
        data = response.json()
        reply_text = data["choices"][0]["message"]["content"].strip()
        return reply_text
    except Exception as e:
        return f"⚠️ LLM Error: {str(e)}"

# Generate Chatbot Response
def generate_response(user_message):
    if is_crisis(user_message):
        return {
            "emotion": "crisis",
            "reply": (
                "I'm really sorry you're feeling this way. You're not alone. "
                "Please reach out right now — in India, call AASRA at 91-9820466726 "
                "or visit findahelpline.com ❤️"
            ),
        }

    if is_explicit(user_message):
        return {
            "emotion": "sensitive",
            "reply": (
                "I can't discuss explicit topics, but I can help you talk about your emotions safely. "
                "Would you like to tell me what's bothering you?"
            ),
        }

    broad_emotion, fine_emotion = detect_emotion(user_message)
    context = list(conversation_memory)[-5:]
    reply = generate_llm_reply(user_message, broad_emotion, fine_emotion, context)

    # Clean LLM artifacts like "(27)", "(17)" from start
    reply = reply.strip()
    reply = re.sub(r'^[\(\[\{]?\d+[\)\]\}]?\s*', '', reply)

    conversation_memory.append({"user": user_message, "bot": reply})
    emotion_memory.append(broad_emotion)

    return {"emotion": broad_emotion, "reply": reply}