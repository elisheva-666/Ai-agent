import sys
import ssl
import os
from dotenv import load_dotenv

# טעינת המפתחות מהקובץ
load_dotenv()

# 1. פתרון "פטיש 5 קילו" לנטפרי - מבטל בדיקות SSL לכל הסביבה
ssl._create_default_https_context = ssl._create_unverified_context
os.environ['CURL_CA_BUNDLE'] = ""
os.environ['PYTHONHTTPSVERIFY'] = "0"

# וידוא עברית בטרמינל
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.cohere import Cohere
import gradio as gr

# 2. מפתח Cohere (תדביקי את שלך כאן)
COHERE_KEY = os.getenv("COHERE_KEY").strip()

# 3. הגדרת מודלים - נקי ובלי httpx_client שיעשה בעיות
print("מגדיר מודלים מול Cohere...")
Settings.llm = Cohere(model="command-r-08-2024", api_key=COHERE_KEY)
Settings.embed_model = CohereEmbedding(model_name="embed-multilingual-v3.0", api_key=COHERE_KEY)

# 4. טעינת מסד הנתונים מהתיקייה המקומית
print("טוען את המידע מהמחשב...")
try:
    storage_context = StorageContext.from_defaults(persist_dir="./storage")
    index = load_index_from_storage(storage_context)
    query_engine = index.as_query_engine()
except Exception as e:
    print(f"שגיאה בטעינת הקבצים: {e}")

# 5. פונקציית הצ'אט
def chat_with_data(user_question):
    try:
        response = query_engine.query(user_question)
        return str(response)
    except Exception as e:
        return f"שגיאה בתקשורת: {str(e)}"

# 6. ממשק Gradio
print("מפעיל ממשק... חפשי את הקישור!")
iface = gr.Interface(
    fn=chat_with_data,
    inputs=gr.Textbox(lines=2, placeholder="שאלי אותי שאלה על הפרויקט...", rtl=True),
    outputs=gr.Textbox(label="תשובה", rtl=True),
    title="צ'אט AI לפרויקט",
)

iface.launch()