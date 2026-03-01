import os
from openai import OpenAI
from dotenv import load_dotenv

# טעינת המשתנים
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

print("--- מתחיל בדיקה ---")

# בדיקה 1: האם המפתח קיים?
if not api_key:
    print("❌ שגיאה: המפתח לא נמצא! בדקי את קובץ ה-.env")
    exit()
else:
    # מדפיס רק את ההתחלה והסוף של המפתח כדי שתוודאי שזה המפתח הנכון
    print(f"✅ המפתח נטען: {api_key[:5]}...{api_key[-4:]}")

# בדיקה 2: האם מצליחים להתחבר ל-OpenAI?
try:
    client = OpenAI(api_key=api_key)
    print("🔄 מנסה לשלוח בקשה ל-OpenAI...")
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "האם אתה שומע אותי?"}],
    )
    
    print("✅ הצלחה! התשובה שהתקבלה:")
    print(response.choices[0].message.content)

except Exception as e:
    print("\n❌ נכשל! הנה פרטי השגיאה המלאים:")
    print(e)