import os, ssl
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Settings
from llama_index.embeddings.cohere import CohereEmbedding
from pinecone import Pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.node_parser import SentenceSplitter
from dotenv import load_dotenv

load_dotenv()

# מעקף נטפרי
ssl._create_default_https_context = ssl._create_unverified_context
os.environ['PYTHONHTTPSVERIFY'] = "0"

# --- שלב המפתחות מה-env ---
COHERE_KEY = os.getenv("COHERE_KEY").strip()
PINECONE_KEY = os.getenv("PINECONE_KEY").strip()
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME").strip()

print("בודק חיבור למודלים...")
Settings.embed_model = CohereEmbedding(model_name="embed-multilingual-v3.0", api_key=COHERE_KEY)

print("טוען קבצים מהתיקייה...")
documents = SimpleDirectoryReader("./my-dummy-project", recursive=True).load_data()
print(f"נטענו {len(documents)} מסמכים.")

print("מתחבר ל-Pinecone...")
pc = Pinecone(api_key=PINECONE_KEY)
pinecone_index = pc.Index(INDEX_NAME)

# הכנת החיבור למסד הנתונים
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
storage_context = StorageContext.from_defaults(vector_store=vector_store) # פה האובייקט האמיתי (s קטנה)

# הגדרת חותך טקסט חכם
node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)

print("מתחיל העלאה לענן (עם חיתוך טקסט משופר)...")
try:
    index = VectorStoreIndex.from_documents(
        documents, 
        storage_context=storage_context, # משתמשים במשתנה שיצרנו
        transformations=[node_parser],   # חותך הטקסט
        show_progress=True
    )
    print("✅✅✅ זה עבד! הנתונים ב-Pinecone!")
except Exception as e:
    print(f"שגיאה בתהליך: {e}")