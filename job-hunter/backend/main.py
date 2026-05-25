from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
from agent import JobHunterAgent
import json

app = FastAPI(title="Job Hunter API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent_instances: dict[str, JobHunterAgent] = {}


class StartSessionRequest(BaseModel):
    cv_text: str
    thread_id: str


class UserChoiceRequest(BaseModel):
    thread_id: str
    approved_indices: list[int]


class ResumeRequest(BaseModel):
    thread_id: str


@app.post("/api/start")
async def start_session(req: StartSessionRequest):
    """Start a new job hunting session with CV text."""
    agent = JobHunterAgent()
    agent_instances[req.thread_id] = agent

    result = await agent.start(req.cv_text, req.thread_id)
    return result


@app.post("/api/approve-sources")
async def approve_sources(req: UserChoiceRequest):
    """User approves/rejects sources found by agent."""
    agent = agent_instances.get(req.thread_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Session not found")

    result = await agent.approve_sources(req.approved_indices, req.thread_id)
    return result


@app.get("/api/session/{thread_id}")
async def get_session(thread_id: str):
    """Get current session state."""
    agent = agent_instances.get(thread_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"state": agent.get_state()}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
