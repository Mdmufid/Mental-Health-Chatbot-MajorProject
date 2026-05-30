# 🧠 An Emotion-Aware Mental Health Chatbot — Major Project

> A full-stack AI-powered mental health web application built with **Flask**, **SQLAlchemy**, **DistilBERT v3**, and **OpenRouter (LLaMA 3.1 70B)**. Features user authentication, persistent conversation history, mood logging, real-time emotion detection, crisis intervention, and a custom HTML/CSS/JavaScript UI.

---

## 📸 Preview

> _Add screenshots of the login page, dashboard, and chat interface here._

---

## 🆚 Minor Project vs Major Project

| Feature | Minor Project | Major Project (this) |
|---|---|---|
| UI | Gradio (simple) | Custom HTML/CSS/JS (full web UI) |
| User Accounts | ❌ | ✅ Register, login, profile |
| Database | ❌ | ✅ SQLite via SQLAlchemy |
| Conversation History | In-memory only | ✅ Persisted to DB per user |
| Mood Logging | ❌ | ✅ MoodLog model |
| Email Support | ❌ | ✅ Flask-Mail (email change tokens) |
| Crisis Detection | ❌ | ✅ Keyword-based safety filter |
| Content Filtering | ❌ | ✅ Explicit content filter |
| DistilBERT Model | v1 | ✅ v3 (improved accuracy) |
| Blueprint Architecture | ❌ | ✅ auth, profile, dashboard, chatbot |
| Project Report | ❌ | ✅ `.docx` + `.pptx` included |

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
  │  DistilBERT v3 Emotion Detector  │  ← local, on-device
  │  emotion_model/models/           │
  │  transformer_model_v3/           │
  │  6 classes: anger / fear / joy / │
  │  love / neutral / sadness        │
  └──────────────┬───────────────────┘
                 │ emotion label
                 ▼
  ┌──────────────────────────────────┐
  │  OpenRouter — LLaMA 3.1 70B      │  ← cloud LLM
  │  System: empathetic companion    │
  │  Context: last 5 messages        │
  │  Temp: 0.8 | Max tokens: 300     │
  └──────────────┬───────────────────┘
                 │
                 ▼
  Reply saved to DB (Message model)
  Conversation emotion updated
  Response returned as JSON → UI
```

---

## ✨ Features

### 🔐 User Authentication
- Register with full name, username, email, and password
- Secure login with hashed passwords (Werkzeug)
- Email change with token-based verification (Flask-Mail)
- Session management with Flask `SECRET_KEY`

### 💬 Chatbot
- **Real-time emotion detection** via fine-tuned DistilBERT v3 (local, no API cost)
- **Emotion-conditioned LLM responses** — LLaMA 3.1 70B adapts tone to detected emotion
- **Rolling 8-message memory** — `deque(maxlen=8)` for both conversation and emotion history
- **Crisis intervention** — detects keywords like "suicide", "kill myself", "self harm" and responds with AASRA helpline
- **Content filtering** — blocks explicit topics and redirects empathetically
- **LLM artifact cleaning** — strips numeric prefixes like `(27)` from replies

### 🗂️ Conversation & History
- Multiple named conversations per user ("New Chat" with auto-title)
- All messages persisted to database with timestamps
- `last_emotion` tracked per conversation
- Dashboard view of conversation history

### 📊 Mood Logging
- Log daily mood (e.g. "happy", "sad") with optional short note
- Mood history stored per user in `MoodLog` table

### 👤 User Profile
- Update profile details
- Change email (with verification token sent by email)

### 🗄️ Database (SQLAlchemy)
- `User` — accounts with hashed passwords and email change tokens
- `Conversation` — named chat sessions linked to users
- `Message` — individual messages with role (user/assistant) and timestamp
- `MoodLog` — mood entries with notes and timestamps
- Auto-creates all tables on first run (`db.create_all()`)

---

## 📁 Project Structure

```
Mental-Health-Chatbot-MajorProject/
│
├── app.py                          # Flask app factory — registers all blueprints
├── chatbot_core.py                 # Core AI logic: emotion detection, LLM calls,
│                                   # safety filters, response generation
├── config.py                       # Flask config: DB URI, secret key, mail settings
├── extensions.py                   # Shared Flask extensions (db, mail)
├── models.py                       # SQLAlchemy models: User, Conversation,
│                                   # Message, MoodLog
├── evaluate_model.py               # DistilBERT model evaluation script
├── requirements.txt                # Full pinned Python dependencies (73 packages)
├── .gitignore
│
├── routes/                         # Flask Blueprints
│   ├── auth.py                     # Register, Login, Logout
│   ├── profile.py                  # Profile view and email change
│   ├── dashboard.py                # Conversation list and mood dashboard
│   └── chatbot.py                  # Chat API endpoint and chat page
│
├── templates/                      # Jinja2 HTML templates
│   ├── base.html                   # Base layout with navbar
│   ├── login.html                  # Login page
│   ├── register.html               # Registration page
│   ├── dashboard.html              # User dashboard
│   ├── chat.html                   # Chat interface
│   └── profile.html                # Profile page
│
├── static/                         # Frontend assets
│   ├── css/
│   │   └── style.css               # Main stylesheet (26% of codebase)
│   └── js/
│       └── chat.js                 # Chat UI logic: send messages, render
│                                   # emotions, update conversation list
│
├── emotion_model/                  # Local DistilBERT v3 model
│   └── models/
│       └── transformer_model_v3/   # Fine-tuned weights & tokenizer
│           ├── config.json
│           ├── pytorch_model.bin
│           ├── tokenizer_config.json
│           ├── vocab.txt
│           └── label_map.json      # {emotion: id} mapping
│
├── An-Emotion-Aware-Mental-Health-Chatbot (1).pptx   # Project presentation
└── MINOR PROJECT REPORT.docx                          # Project report document
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Web Framework | Flask 3.1.3 |
| Database ORM | Flask-SQLAlchemy 3.1.1 + SQLite |
| Authentication | Werkzeug password hashing + Flask sessions |
| Email | Flask-Mail 0.10.0 (Gmail SMTP) |
| Emotion Detection | DistilBERT v3 (`transformers` 5.3.0 + PyTorch) |
| LLM Backend | Meta LLaMA 3.1 70B Instruct via OpenRouter |
| ML / Data | scikit-learn, pandas, datasets, numpy |
| Frontend | HTML5 + CSS3 + JavaScript (custom, no framework) |
| Templating | Jinja2 |
| Config | python-dotenv |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- An [OpenRouter](https://openrouter.ai/) API key (free tier available)
- Gmail account for email features (or any SMTP provider)
- The `emotion_model/models/transformer_model_v3/` folder with trained weights

### 1. Clone the Repository

```bash
git clone https://github.com/Mdmufid/Mental-Health-Chatbot-MajorProject.git
cd Mental-Health-Chatbot-MajorProject
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> **GPU note:** The `requirements.txt` includes commented-out CUDA torch lines. For CPU-only use, the default `torch` install works fine. For GPU acceleration, uncomment and install:
> ```
> torch==2.6.0+cu124
> torchaudio==2.6.0+cu124
> torchvision==0.21.0+cu124
> ```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Flask
SECRET_KEY=your_strong_secret_key_here

# Database (SQLite default, or use PostgreSQL)
DATABASE_URL=sqlite:///app.db

# OpenRouter AI
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
MODEL_PATH=emotion_model/models/transformer_model_v3

# Email (Flask-Mail via Gmail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_gmail_address@gmail.com
MAIL_PASSWORD=your_gmail_app_password
MAIL_DEFAULT_SENDER=your_gmail_address@gmail.com
```

> **Gmail tip:** Use an [App Password](https://support.google.com/accounts/answer/185833) rather than your main password if 2FA is enabled.

### 5. Run the App

```bash
python app.py
```

On first run, Flask will automatically call `db.create_all()` and create `app.db` with all tables. Open your browser at:

```
http://localhost:5000
```

You will be redirected to the login page. Register a new account to get started.

---

## 🔌 Application Routes

| Blueprint | Route | Method | Description |
|---|---|---|---|
| `auth` | `/login` | GET, POST | User login |
| `auth` | `/register` | GET, POST | New user registration |
| `auth` | `/logout` | GET | Log out current user |
| `profile` | `/profile` | GET, POST | View and update profile |
| `profile` | `/change-email` | POST | Request email change (sends token) |
| `dashboard` | `/dashboard` | GET | Conversation list + mood overview |
| `dashboard` | `/mood` | POST | Log a new mood entry |
| `chatbot` | `/chat` | GET | Chat interface page |
| `chatbot` | `/chat/send` | POST | Send a message, get AI reply (JSON) |
| `chatbot` | `/chat/history/<id>` | GET | Load a specific conversation |

---

## 🗄️ Database Models

```
User
 ├── id, fullname, email, username, password_hash
 ├── pending_email, email_change_token
 ├── conversations → [Conversation]
 └── mood_logs     → [MoodLog]

Conversation
 ├── id, title, user_id, last_emotion
 ├── created_at, updated_at
 └── messages → [Message]

Message
 ├── id, conversation_id, user_id
 ├── role ("user" | "assistant")
 ├── content, created_at
 └── user → User

MoodLog
 ├── id, user_id, mood, note
 └── logged_at
```

---

## 🎭 Emotion Classes

The DistilBERT v3 model classifies messages into six emotions:

| ID | Emotion | Example |
|----|---------|---------|
| 0 | `anger` | "I'm so frustrated and angry right now" |
| 1 | `fear` | "I'm scared about what might happen" |
| 2 | `joy` | "I'm feeling really happy today!" |
| 3 | `love` | "I miss my family so much" |
| 4 | `neutral` | "Can you tell me about anxiety?" |
| 5 | `sadness` | "I've been feeling really low lately" |

---

## 🚨 Safety Features

The chatbot includes built-in safety filters that activate before any LLM call:

**Crisis Detection** — triggers on keywords like `suicide`, `kill myself`, `end my life`, `want to die`, `self harm`:
```
"I'm really sorry you're feeling this way. You're not alone.
Please reach out right now — in India, call AASRA at 91-9820466726
or visit findahelpline.com ❤️"
```

**Content Filter** — redirects explicit language back to emotional support.

---

## 🔒 Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ | Flask session signing key |
| `DATABASE_URL` | ❌ | SQLAlchemy DB URI (default: `sqlite:///app.db`) |
| `OPENROUTER_API_KEY` | ✅ | OpenRouter API key |
| `OPENROUTER_BASE_URL` | ❌ | OpenRouter base URL |
| `MODEL_PATH` | ❌ | Path to DistilBERT v3 model directory |
| `MAIL_SERVER` | ❌ | SMTP server (default: `smtp.gmail.com`) |
| `MAIL_PORT` | ❌ | SMTP port (default: `587`) |
| `MAIL_USE_TLS` | ❌ | Enable TLS (default: `True`) |
| `MAIL_USERNAME` | ✅* | Email address for sending |
| `MAIL_PASSWORD` | ✅* | Email/app password |
| `MAIL_DEFAULT_SENDER` | ✅* | Default from address |

> *Required only if using email change / verification features.

---

## 📄 Project Documents

The repository includes the full academic deliverables for the major project:

- **`An-Emotion-Aware-Mental-Health-Chatbot (1).pptx`** — Project presentation slides
- **`MINOR PROJECT REPORT.docx`** — Written project report

---

## ⚠️ Disclaimer

This application is an **academic major project** built for educational and research purposes. It is **not** a substitute for professional mental health advice, diagnosis, or treatment.

If you or someone you know is experiencing a mental health crisis, please contact a qualified mental health professional or one of these helplines:

- 🇮🇳 **AASRA (India):** 91-9820466626 (24/7)
- 🇮🇳 **iCall:** 9152987821
- 🌐 **International:** [findahelpline.com](https://findahelpline.com)

---

## 🤝 Contributing

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push to your branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is open source and free to use for educational purposes.

---

## 👤 Author

**Md Mufid Alam**
GitHub: [@Mdmufid](https://github.com/Mdmufid)
