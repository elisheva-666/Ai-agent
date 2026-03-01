import os
import gradio as gr
import httpx  # ספרייה לתקשורת (היא מותקנת אוטומטית עם openai)
from openai import OpenAI
from dotenv import load_dotenv

# 1. טעינת משתני סביבה
load_dotenv()

# הגדרת המפתח
api_key = os.getenv("OPENAI_API_KEY")

# ==========================================
# 🛠️ התיקון לנטפרי (Netfree Fix)
# אנחנו יוצרים "לקוח תקשורת" שמבטל את בדיקת האבטחה (SSL)
# כדי שנטפרי לא יחסום את החיבור.
# ==========================================
http_client = httpx.Client(verify=False)

# יצירת הלקוח של OpenAI עם התיקון שלנו
if api_key:
    client = OpenAI(api_key=api_key, http_client=http_client)
else:
    client = None
    print("Warning: OPENAI_API_KEY not found.")

# ==========================================
# 🛑 SYSTEM PROMPT - כאן את משנה את ההוראות למודל
# ==========================================
SYSTEM_PROMPT = """
You are a Command Line Interface (CLI) expert.
Your task is to translate natural language instructions into Windows Command Prompt (cmd) commands.

Rules:
1. Return ONLY the command itself.
2. Do not include explanations, markdown, or code blocks.
3. If the request is dangerous (like deleting system files), return "BLOCKED".
"""

def process_command(user_input):
    """
    פונקציה שמקבלת את הטקסט מהמשתמש ושולחת ל-OpenAI
    """
    if not client:
        return "שגיאה: חסר מפתח API בקובץ .env"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ],
            temperature=0
        )
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"Error: {str(e)}"

# --- בניית הממשק עם Gradio ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 CLI Agent (Netfree Compatible)")
    gr.Markdown("הכניסי הוראה בשפה טבעית וקבלי פקודת Windows CLI.")
    
    with gr.Row():
        input_text = gr.Textbox(label="הוראה", placeholder="למשל: תציג את כל הקבצים בתיקייה")
        output_text = gr.Code(label="פקודה", language="shell")
    
    submit_btn = gr.Button("תרגם לפקודה", variant="primary")
    
    # חיבור הכפתור לפונקציה
    submit_btn.click(fn=process_command, inputs=input_text, outputs=output_text)

# הרצה
if __name__ == "__main__":
    demo.launch()