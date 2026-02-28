# 🔍 VerifyAI — Fake News Detector for Students

An AI-powered fake news detection web app built with **Streamlit** and **Google Gemini**. Designed to help students develop critical media literacy skills.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 AI Analysis | Gemini 1.5 Flash evaluates credibility holistically |
| 📊 Credibility Score | 0–100 score with visual indicator |
| 🚩 Red Flag Detection | Identifies misleading patterns, emotional language |
| 🔎 Claim Assessment | Breaks down key claims as Likely True / Uncertain / Likely False |
| 📋 Neutral Summary | Unbiased 2–3 sentence summary of the article |
| 📚 Student Tips | Custom recommendations on how to verify the specific article |
| 📥 JSON Export | Download full analysis report |
| 🕓 History | Sidebar shows recent checks with scores |

---

## 🚀 Getting Started

### 1. Clone / Download
```bash
git clone <your-repo>
cd fake-news-detector
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Get a Gemini API Key
- Go to [Google AI Studio](https://aistudio.google.com)
- Create a free API key (no billing required for free tier)

### 4. Run the app
```bash
streamlit run app.py
```

### 5. Use the app
- Enter your Gemini API key in the sidebar
- Paste any article, headline, or social media post
- Click **Analyze Article**

---

## 📁 Project Structure

```
fake-news-detector/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## 🎨 Tech Stack

- **Frontend**: Streamlit with custom CSS (dark theme, Space Mono + Syne fonts)
- **AI Backend**: Google Gemini 1.5 Flash
- **Language**: Python 3.9+

---

## 📊 How the Score Works

| Score Range | Verdict | Meaning |
|---|---|---|
| 0 – 34 | 🚨 LIKELY FAKE | Strong indicators of misinformation |
| 35 – 64 | ⚠️ MISLEADING / UNVERIFIED | Questionable claims or missing context |
| 65 – 100 | ✅ MOSTLY CREDIBLE / CREDIBLE | Passes credibility checks |

---

## 🏫 Educational Use

This tool is designed for:
- Media literacy classes
- Journalism and communications courses
- Critical thinking exercises
- Individual research verification

> **Disclaimer**: This is an AI tool and should not be the sole source of verification. Always cross-check with established fact-checkers like Snopes, PolitiFact, or FactCheck.org.

---

## 🔑 Environment Variable (Optional)
Instead of entering the API key every time, set it as an environment variable:
```bash
export GOOGLE_API_KEY="your-api-key-here"
```
Then modify `app.py` to read `os.environ.get("GOOGLE_API_KEY")` as default.

---

## 📜 License
MIT — Free to use and modify for educational purposes.
