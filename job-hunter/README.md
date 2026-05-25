# 🎯 Job Hunter AI — עוזר חיפוש עבודה חכם

> Agent חכם שמנתח את קורות החיים שלך ומחפש משרות מותאמות אישית בעשרות אתרי דרושים — עם Human-in-the-Loop לאישור המקורות.

## ✨ מה הפרויקט עושה

1. **מקבל קורות חיים** — המשתמש מדביק את ה-CV שלו
2. **Agent חופשי** — ה-Agent מחליט בעצמו אילו שאילתות חיפוש להריץ (4-8 חיפושים שונים)
3. **Human-in-the-Loop** — המשתמש רואה את כל המשרות שנמצאו ומאשר אילו לכלול
4. **סיכום AI** — הAgent מייצר סיכום מותאם אישית בעברית

## 🛠️ טכנולוגיות

| שכבה | טכנולוגיה |
|------|------------|
| Backend | Python + FastAPI |
| AI Agent | LangChain + LangGraph |
| חיפוש | Tavily Search API |
| LLM | OpenAI GPT-4o-mini |
| Frontend | React + TypeScript + Vite |
| HITL | LangGraph MemorySaver Checkpointer |

## 🚀 הרצה מקומית

### דרישות מוקדמות
- Python 3.11+
- Node.js 18+
- [OpenAI API Key](https://platform.openai.com/api-keys)
- [Tavily API Key](https://tavily.com) — **1,000 חיפושים חינם בחודש**

### Backend

```bash
cd backend

# צור סביבה וירטואלית
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# התקן תלויות
pip install -r requirements.txt

# הגדר משתני סביבה
cp .env.example .env
# ערוך את .env והכנס את המפתחות שלך

# הרץ
python main.py
```

השרת יעלה על `http://localhost:8000`

### Frontend

```bash
cd frontend

npm install
npm run dev
```

האפליקציה תהיה זמינה על `http://localhost:3000`

## 📁 מבנה הפרויקט

```
job-hunter/
├── backend/
│   ├── main.py          # FastAPI server
│   ├── agent.py         # LangChain Agent + LangGraph
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── App.tsx           # Main app + state machine
    │   ├── components/
    │   │   ├── CVInput.tsx       # שלב 1 - הכנסת CV
    │   │   ├── SearchingAnimation.tsx  # אנימציה בזמן חיפוש
    │   │   ├── SourceSelector.tsx     # שלב HITL - בחירת מקורות
    │   │   └── Summary.tsx           # שלב סיכום סופי
    │   └── hooks/
    │       └── useApi.ts     # API calls
    └── package.json
```

## 💡 דוגמאות לשימוש

**מפתח Full Stack:**
```
3 שנות ניסיון ב-React, Node.js, TypeScript
PostgreSQL, Docker, AWS
```

**Data Scientist:**
```
Python, Pandas, PyTorch, scikit-learn
ניסיון ב-NLP ו-Computer Vision
```

**DevOps Engineer:**
```
Kubernetes, Terraform, Jenkins, GitLab CI
AWS/GCP certified
```

## 🏗️ ארכיטקטורה

```
User → React UI → FastAPI → LangGraph Agent
                              ↓
                         TavilySearch (x4-8)
                              ↓
                         Parse Sources
                              ↓
                    [HITL: User Approves]
                              ↓
                         GPT-4o Summarize
                              ↓
                         React UI ← Summary
```

## 📝 הערות

- ה-Agent פועל באוטונומיה מלאה בשלב החיפוש
- MemorySaver שומר את ה-state לאורך כל הסשן
- HITL מיושם בין שלב החיפוש לסיכום
