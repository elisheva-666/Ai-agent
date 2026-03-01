from pydantic import BaseModel
from typing import Optional, List
import uuid

# הגדרת הישות - משימה
class Task(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    task_type: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: str = "open"

# מסד הנתונים שלנו (מערך בזיכרון)
tasks_db: List[Task] = []

def get_tasks(status: Optional[str] = None) -> List[Task]:
    if status:
        return [task for task in tasks_db if task.status == status]
    return tasks_db

def add_task(title: str, description: str = "", start_date: str = "", end_date: str = "") -> Task:
    new_task = Task(
        id=str(uuid.uuid4()),
        title=title,
        description=description,
        start_date=start_date,
        end_date=end_date
    )
    tasks_db.append(new_task)
    return new_task

def update_task(task_id: str, status: str) -> Optional[Task]:
    for task in tasks_db:
        if task.id == task_id:
            task.status = status
            return task
    return None

def delete_task(task_id: str) -> bool:
    global tasks_db
    tasks_db = [task for task in tasks_db if task.id != task_id]
    return True