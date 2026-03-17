from llama_index.utils.workflow import draw_all_possible_flows
from workflow_app import RAGWorkflow 

print("מייצר תרשים זרימה...")

# 1. יוצרים מופע אמיתי של ה-Workflow שלנו
my_workflow = RAGWorkflow(timeout=60)

# 2. מעבירים את המופע לפונקציית הציור (ולא את המחלקה עצמה)
draw_all_possible_flows(my_workflow, filename="workflow_graph.html")

print("✅ נוצר קובץ בשם workflow_graph.html!")