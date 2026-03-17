import os, ssl
import gradio as gr
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.workflow import Event, StartEvent, StopEvent, Workflow, step
from llama_index.llms.cohere import Cohere
from llama_index.embeddings.cohere import CohereEmbedding
from pinecone import Pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.llms import ChatMessage
from dotenv import load_dotenv

load_dotenv()

# 1. הגדרות נטפרי
ssl._create_default_https_context = ssl._create_unverified_context
os.environ['CURL_CA_BUNDLE'] = ""

COHERE_KEY = os.getenv("COHERE_KEY").strip()
PINECONE_KEY = os.getenv("PINECONE_KEY").strip()
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME").strip()

Settings.llm = Cohere(model="command-r-08-2024", api_key=COHERE_KEY)
Settings.embed_model = CohereEmbedding(model_name="embed-multilingual-v3.0", api_key=COHERE_KEY)

# אירועים
class RetrievalEvent(Event):
    context: str
    query: str
    confidence: float # הוספנו מדד ביטחון

class RAGWorkflow(Workflow):
    @step
    async def validate_input(self, ev: StartEvent) -> StartEvent | StopEvent:
        """ולידציה 1: בדיקת קלט ריק או קצר מדי"""
        if not ev.query or len(ev.query.strip()) < 3:
            return StopEvent(result="השאלה קצרה מדי, בבקשה תפרטי יותר.")
        return ev

    @step
    async def retrieve(self, ev: StartEvent) -> RetrievalEvent | StopEvent:
        """שלב השליפה עם בדיקת איכות"""
        pc = Pinecone(api_key=PINECONE_KEY)
        index = pc.Index(INDEX_NAME)
        vector_store = PineconeVectorStore(pinecone_index=index)
        query_index = VectorStoreIndex.from_vector_store(vector_store)
        
        retriever = query_index.as_retriever(similarity_top_k=3)
        nodes = retriever.retrieve(ev.query)
        
        if not nodes or nodes[0].get_score() < 0.3: # ולידציה 2: האם המידע רלוונטי?
            return StopEvent(result="מצטערת, לא מצאתי מידע רלוונטי בקבצי הפרויקט לגבי זה.")

        context = "\n".join([n.get_content() for n in nodes])
        return RetrievalEvent(context=context, query=ev.query, confidence=nodes[0].get_score())

    @step
    async def generate(self, ev: RetrievalEvent) -> StopEvent:
        """שלב הניסוח"""
        messages = [
            ChatMessage(role="system", content=f"ענה על השאלה. (רמת ביטחון במידע: {ev.confidence:.2f})"),
            ChatMessage(role="user", content=f"מידע: {ev.context}\nשאלה: {ev.query}")
        ]
        response = Settings.llm.chat(messages)
        return StopEvent(result=str(response.message.content))

# חיבור ל-Gradio
async def run_chat(message, history):
    w = RAGWorkflow(timeout=60)
    return await w.run(query=message)

demo = gr.ChatInterface(fn=run_chat, title="Advanced RAG Workflow")

if __name__ == "__main__":
    demo.launch()