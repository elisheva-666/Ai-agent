from llama_index.core import SimpleDirectoryReader

print("--- מתחיל סריקה של התיקייה my-dummy-project ---")
try:
    reader = SimpleDirectoryReader("./my-dummy-project", recursive=True)
    documents = reader.load_data()
    
    print(f"\nהצלחה! פייתון מצא {len(documents)} מקטעי טקסט.")
    print("רשימת הקבצים שהוא קרא:")
    
    # מדפיס את השמות של כל הקבצים שהוא קלט
    for i, doc in enumerate(documents):
        file_name = doc.metadata.get('file_name', 'קובץ ללא שם')
        print(f"[{i+1}] {file_name}")
        
except Exception as e:
    print(f"\nשגיאה בקריאת התיקייה: {e}")