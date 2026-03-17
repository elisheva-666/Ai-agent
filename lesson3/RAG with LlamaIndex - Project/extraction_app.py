import os, ssl, json
from llama_index.core import SimpleDirectoryReader, Settings, PromptTemplate
from llama_index.llms.cohere import Cohere
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv

load_dotenv()

# מעקף נטפרי
ssl._create_default_https_context = ssl._create_unverified_context
os.environ['PYTHONHTTPSVERIFY'] = "0"

COHERE_KEY = os.getenv("COHERE_KEY").strip()
# מומלץ להשתמש במודל החזק ביותר לחילוץ נתונים
Settings.llm = Cohere(model="command-r-plus", api_key=COHERE_KEY)

# 1. הגדרת הסכמה
class Decision(BaseModel):
    title: str = Field(description="כותרת ההחלטה")
    summary: str = Field(description="סיכום קצר של ההחלטה")
    tags: List[str] = Field(description="תגיות רלוונטיות")

class Rule(BaseModel):
    rule: str = Field(description="החוק או ההנחיה")
    scope: str = Field(description="תחום (UI, Security, וכו')")

class ExtractionSchema(BaseModel):
    decisions: List[Decision]
    rules: List[Rule]

# 2. יצירת תבנית הפרומפט בצורה ש-LlamaIndex אוהב
extraction_template = PromptTemplate(
    "קרא את הטקסט הבא וחלץ מתוכו החלטות טכניות וחוקי מערכת.\n"
    "הטקסט:\n{text}\n"
)

def extract_structured_data():
    print("מתחיל לסרוק קבצים לחילוץ נתונים מובנים...")
    documents = SimpleDirectoryReader("./my-dummy-project", recursive=True).load_data()
    
    all_extracted_data = {"decisions": [], "rules": []}
    
    for doc in documents:
        print(f"מעבד את הקובץ: {doc.metadata.get('file_name')}...")
        
        try:
            # כאן התיקון: אנחנו מעבירים את התבנית ואת הטקסט בנפרד
            response = Settings.llm.structured_predict(
                ExtractionSchema, 
                extraction_template, 
                text=doc.text
            )
            
            all_extracted_data["decisions"].extend([d.dict() for d in response.decisions])
            all_extracted_data["rules"].extend([r.dict() for r in response.rules])
        except Exception as e:
            print(f"שגיאה בעיבוד קובץ {doc.metadata.get('file_name')}: {e}")

    # 3. שמירה לקובץ
    with open("extracted_data.json", "w", encoding="utf-8") as f:
        json.dump(all_extracted_data, f, ensure_ascii=False, indent=4)
    
    print("\n✅ הצלחה! הקובץ extracted_data.json נוצר.")

if __name__ == "__main__":
    extract_structured_data()