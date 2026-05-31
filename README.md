---
title: Mental Health Chatbot
emoji: 🧠
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
app_port: 7860
---

# 🧠 An Emotion-Aware Mental Health Chatbot — Major Project

> A full-stack AI-powered mental health web application built with **Flask**, **SQLAlchemy**, **DistilBERT v3**, and **OpenRouter (LLaMA 3.1 70B)**. Features user authentication, persistent conversation history, mood logging, real-time emotion detection, crisis intervention, and a custom HTML/CSS/JavaScript UI — deployed live on **Hugging Face Spaces** with **Neon PostgreSQL**.

🔗 **Live Demo:** [huggingface.co/spaces/MdMufid/mental-health-chatbot](https://huggingface.co/spaces/MdMufid/mental-health-chatbot)
🤗 **Emotion Model:** [huggingface.co/MdMufid/mental-health-emotion-model](https://huggingface.co/MdMufid/mental-health-emotion-model)

---

## 📸 Preview

> _Add screenshots of the login page, dashboard, and chat interface here._

---

## 🆚 Minor Project vs Major Project

| Feature | Minor Project | Major Project (this) |
|---|---|---|
| UI | Gradio (simple) | Custom HTML/CSS/JS (full web UI) |
| User Accounts | ❌ | ✅ Register, login, profile |
| Database | ❌ | ✅ Neon PostgreSQL via SQLAlchemy |
| Conversation History | In-memory only | ✅ Persisted to DB per user |
| Mood Logging | ❌ | ✅ MoodLog model |
| Email Support | ❌ | ✅ Flask-Mail (password reset) |
| Crisis Detection | ❌ | ✅ Keyword-based safety filter |
| Content Filtering | ❌ | ✅ Explicit content filter |
| DistilBERT Model | v1 | ✅ v3 (improved accuracy) |
| Blueprint Architecture | ❌ | ✅ auth, profile, dashboard, chatbot |
| Deployment | Local only | ✅ Live on Hugging Face Spaces |

---

## 🏗️ How It Works

```
 User sends message (authenticated)
          │
          ▼
  ┌──────────────────────────────────┐
  │     Safety Filters (chatbot_core)│
  │  Crisis keywords → helpline msg  │
  │  Explicit content → redirect     │
  └──────────────┬───────────────────┘
                 │ passes filters
                 ▼
  ┌──────────────────────────────────┐
  │  DistilBERT v3 Emotion Detector  │  ← loaded from HF Hub
  │  MdMufid/mental-health-emotion-  │
  │  model                           │
  │  6 classes: anger / fear / joy / │
  │  love / neutral / sadness        │
  └──────────────┬───────────────────┘
                 │ emotion label
                 ▼
  ┌──────────────────────────────────┐
  │  OpenRouter — LLaMA 3.1 70B      │  ← cloud LLM
  │  System: empathetic companion    │
  │  Context: last 8 messages        │
  │  Temp: 0.8 | Max tokens: 300     │
  └──────────────┬───────────────────┘
                 │
                 ▼
  Reply saved to Neon PostgreSQL
  Response returned as JSON → UI
```

---

## ✨ Features

### 🔐 User Authentication
- Register with full name, username, email, and password
- Secure login with Werkzeug hashed passwords
- Password reset via email token (Flask-Mail)
- Email change with token-based verification
- Persistent sessions with ProxyFix for Hugging Face Spaces

### 💬 Chatbot
- **Real-time emotion detection** via fine-tuned DistilBERT v3 (loaded from HF Hub)
- **Emotion-conditioned LLM responses** — LLaMA 3.1 70B adapts tone to detected emotion
- **Rolling 8-message memory** for conversational context
- **Crisis intervention** — detects keywords and responds with AASRA helpline
- **Content filtering** — blocks explicit topics empathetically

### 🗂️ Conversation & History
- Multiple named conversations per user
- All messages persisted to Neon PostgreSQL
- `last_emotion` tracked per conversation
- Dashboard view of all conversation history

### 📊 Mood Logging
- Log daily mood with optional notes
- Mood history stored per user

### 👤 User Profile
- Update profile details
- Change email with verification token

---

## 📁 Project Structure

```
Mental-Health-Chatbot-MajorProject/
│
├── app.py                          # Flask app factory with ProxyFix
├── chatbot_core.py                 # Emotion detection + LLM + safety filters
├── config.py                       # Flask config with Neon PostgreSQL pool settings
├── extensions.py                   # Shared Flask extensions (db, mail)
├── models.py                       # SQLAlchemy models: User, Conversation,
│                                   # Message, MoodLog
├── evaluate_model.py               # DistilBERT model evaluation script
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker config for HF Spaces (port 7860)
├── .gitignore
│
├── routes/                         # Flask Blueprints
│   ├── auth.py                     # Register, Login, Logout, Password Reset
│   ├── profile.py                  # Profile view and email change
│   ├── dashboard.py                # Conversation list and mood dashboard
│   └── chatbot.py                  # Chat API endpoint and chat page
│
├── templates/                      # Jinja2 HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── chat.html
│   ├── profile.html
│   ├── forgot-password.html
│   └── reset-password.html
│
└── static/                         # Frontend assets
    ├── css/style.css
    └── js/
        ├── chatbot.js
        └── change-password.js
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Web Framework | Flask 3.1.3 + Werkzeug ProxyFix |
| Database | Neon PostgreSQL + Flask-SQLAlchemy 3.1.1 |
| Authentication | Werkzeug password hashing + Flask sessions |
| Email | Flask-Mail 0.10.0 (Gmail SMTP) |
| Emotion Detection | DistilBERT v3 via Hugging Face Hub |
| LLM Backend | Meta LLaMA 3.1 70B via OpenRouter |
| ML Framework | PyTorch + Transformers |
| Frontend | HTML5 + CSS3 + JavaScript (custom) |
| Containerisation | Docker |
| Deployment | Hugging Face Spaces (CPU Basic, free) |
| Config | python-dotenv |

---

## 🚀 Getting Started Locally

### Prerequisites
- Python 3.9+
- An [OpenRouter](https://openrouter.ai/) API key
- Gmail account for email features

### 1. Clone the Repository

```bash
git clone https://github.com/Mdmufid/Mental-Health-Chatbot-MajorProject.git
cd Mental-Health-Chatbot-MajorProject
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your_strong_secret_key_here
DATABASE_URL=sqlite:////app/instance/app.db
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
MODEL_PATH=MdMufid/mental-health-emotion-model
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_gmail@gmail.com
MAIL_PASSWORD=your_gmail_app_password
MAIL_DEFAULT_SENDER=your_gmail@gmail.com
```

### 5. Run the App

```bash
python app.py
```

Open your browser at `http://localhost:5000`

---

## ☁️ Deployment (Hugging Face Spaces)

This project is deployed live on Hugging Face Spaces using Docker + Neon PostgreSQL.

### Environment Secrets Required on HF Spaces

Go to your Space → **Settings** → **Repository Secrets** and add:

| Secret | Value |
|---|---|
| `SECRET_KEY` | any long random string |
| `DATABASE_URL` | your Neon PostgreSQL connection string |
| `OPENROUTER_API_KEY` | your OpenRouter API key |
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` |
| `MODEL_PATH` | `MdMufid/mental-health-emotion-model` |
| `MAIL_USERNAME` | your Gmail address |
| `MAIL_PASSWORD` | your Gmail App Password |
| `MAIL_DEFAULT_SENDER` | your Gmail address |

### Push to HF Spaces

```bash
git remote add space https://YOUR_HF_TOKEN@huggingface.co/spaces/MdMufid/mental-health-chatbot
git push space main
```

---

## 🗄️ Database Models

```
User
 ├── id, fullname, email (VARCHAR 200)
 ├── username (VARCHAR 200)
 ├── password_hash (VARCHAR 500)   ← sized for scrypt hashes
 ├── pending_email, email_change_token (VARCHAR 500)
 ├── conversations → [Conversation]
 └── mood_logs     → [MoodLog]

Conversation
 ├── id, title, user_id, last_emotion
 ├── created_at, updated_at
 └── messages → [Message]

Message
 ├── id, conversation_id, user_id
 ├── role ("user" | "assistant")
 └── content, created_at

MoodLog
 ├── id, user_id, mood, note
 └── logged_at
```

---

## 🔌 Application Routes

| Blueprint | Route | Method | Description |
|---|---|---|---|
| `auth` | `/login` | GET, POST | User login |
| `auth` | `/register` | GET, POST | New user registration |
| `auth` | `/logout` | GET | Log out |
| `auth` | `/forgot-password` | GET, POST | Request password reset email |
| `auth` | `/reset-password/<token>` | GET, POST | Reset password via token |
| `profile` | `/profile` | GET, POST | View and update profile |
| `profile` | `/change-email` | POST | Request email change |
| `dashboard` | `/dashboard` | GET | Conversation list + mood |
| `dashboard` | `/mood` | POST | Log a mood entry |
| `chatbot` | `/chat` | GET | Chat interface |
| `chatbot` | `/chat/send` | POST | Send message, get AI reply |
| `chatbot` | `/chat/history/<id>` | GET | Load a conversation |

---

## 🎭 Emotion Classes

| ID | Emotion | Example |
|----|---------|---------|
| 0 | `anger` | "I'm so frustrated right now" |
| 1 | `fear` | "I'm scared about what might happen" |
| 2 | `joy` | "I'm feeling really happy today!" |
| 3 | `love` | "I miss my family so much" |
| 4 | `neutral` | "Can you tell me about anxiety?" |
| 5 | `sadness` | "I've been feeling really low lately" |

---

## 🚨 Safety Features

**Crisis Detection** — triggers on keywords like `suicide`, `kill myself`, `end my life`:
> "I'm really sorry you're feeling this way. You're not alone. Please reach out — in India, call AASRA at 91-9820466726 ❤️"

**Content Filter** — redirects explicit language back to emotional support.

---

## 🔒 Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ | Flask session signing key |
| `DATABASE_URL` | ✅ | Neon PostgreSQL connection string |
| `OPENROUTER_API_KEY` | ✅ | OpenRouter API key |
| `OPENROUTER_BASE_URL` | ❌ | OpenRouter base URL |
| `MODEL_PATH` | ❌ | HF Hub model ID (default: `MdMufid/mental-health-emotion-model`) |
| `MAIL_USERNAME` | ✅* | Gmail address for sending emails |
| `MAIL_PASSWORD` | ✅* | Gmail App Password |
| `MAIL_DEFAULT_SENDER` | ✅* | Default from address |

---

## ⚠️ Disclaimer

This application is an **academic major project** built for educational and research purposes. It is **not** a substitute for professional mental health advice, diagnosis, or treatment.

If you or someone you know is experiencing a mental health crisis:

- 🇮🇳 **AASRA (India):** 91-9820466627 (24/7)
- 🇮🇳 **iCall:** 9152987821
- 🌐 **International:** [findahelpline.com](https://findahelpline.com)

---

## 🤝 Contributing

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is open source and free to use for educational purposes.

---

## 👤 Author

**Md Mufid Alam**
GitHub: [@Mdmufid](https://github.com/Mdmufid)
Hugging Face: [@MdMufid](https://huggingface.co/MdMufid)
