import json
import os
import httpx # הוספנו את זה
from dotenv import load_dotenv
from openai import OpenAI
import todo_service

# טעינת משתני הסביבה (מפתח ה-API) מהקובץ .env
load_dotenv()

# אתחול הלקוח של OpenAI עם הגדרה לעקוף את שגיאת התעודה של נטפרי
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    http_client=httpx.Client(verify=False) # הוספנו את השורה הזו
)

def run_agent(query: str) -> str:
    # 1. הגדרת הפונקציות (Tools) שה-Agent יכול להשתמש בהן
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_tasks",
                "description": "שולף את רשימת המשימות במערכת. אפשר לסנן לפי סטטוס.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "description": "סטטוס המשימה (למשל 'open', 'done', 'in_progress')"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "מוסיף משימה חדשה למערכת",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "כותרת או שם המשימה"},
                        "description": {"type": "string", "description": "תיאור מורחב של המשימה (אופציונלי)"},
                        "start_date": {"type": "string", "description": "תאריך התחלה (אופציונלי)"},
                        "end_date": {"type": "string", "description": "תאריך סיום או יעד (אופציונלי)"}
                    },
                    "required": ["title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "מעדכן סטטוס של משימה קיימת",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "המזהה הייחודי (ID) של המשימה"},
                        "status": {"type": "string", "description": "הסטטוס החדש של המשימה"}
                    },
                    "required": ["task_id", "status"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "מוחק משימה מהמערכת לפי המזהה שלה",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "המזהה הייחודי (ID) של המשימה למחיקה"}
                    },
                    "required": ["task_id"]
                }
            }
        }
    ]

    # יצירת היסטוריית ההודעות (מתחילים עם הנחיית מערכת והבקשה של המשתמש)
    messages = [
        {"role": "system", "content": "אתה עוזר וירטואלי חכם, ידידותי ויעיל לניהול משימות. תפקידך להבין את בקשת המשתמש, להפעיל את הפונקציות המתאימות במערכת (הוספה, מחיקה, עדכון או שליפה), ולאחר מכן לענות למשתמש בצורה נעימה וטבעית בעברית."},
        {"role": "user", "content": query}
    ]

    # 2. שליחת הבקשה ל-GPT עם הגדרת הכלים
    response = client.chat.completions.create(
        model="gpt-4o-mini", # אפשר גם להשתמש ב-gpt-4o-mini שהוא מהיר וזול יותר
        messages=messages,
        tools=tools
    )

    response_message = response.choices[0].message

    # 3. בדיקה אם GPT החליט שצריך להפעיל פונקציה
    if response_message.tool_calls:
        # מוסיפים את תגובת המודל (שכוללת את הבקשה להפעלת הפונקציה) להיסטוריה
        messages.append(response_message)

        # מעבר על כל הפונקציות ש-GPT ביקש להפעיל (יכולות להיות כמה במקביל)
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            # 4. הפעלת הפונקציה המתאימה מקובץ ה-todo_service שלנו
            result = None
            if function_name == "get_tasks":
                tasks = todo_service.get_tasks(**function_args)
                result = [task.model_dump() for task in tasks] # המרה למילון כדי ש-GPT יבין
            
            elif function_name == "add_task":
                task = todo_service.add_task(**function_args)
                result = task.model_dump()
            
            elif function_name == "update_task":
                task = todo_service.update_task(**function_args)
                result = task.model_dump() if task else {"error": "Task not found"}
            
            elif function_name == "delete_task":
                success = todo_service.delete_task(**function_args)
                result = {"success": success}

            # הוספת התוצאה של הפונקציה בחזרה להיסטוריית ההודעות
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": json.dumps(result, ensure_ascii=False)
            })

        # 5. פנייה שנייה ל-GPT: עכשיו כשיש לו את התוצאות מהמערכת שלנו, הוא ינסח תשובה אנושית
        second_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        
        return second_response.choices[0].message.content

    else:
        # אם GPT החליט שאין צורך להפעיל פונקציה (למשל אם שאלת משהו כללי), פשוט נחזיר את התשובה שלו
        return response_message.content