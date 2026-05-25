import os
import json
from typing import Annotated, TypedDict, Any
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv

load_dotenv()


# ── State ─────────────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    cv_text: str
    found_sources: list[dict]          # [{title, url, snippet, approved}]
    approved_sources: list[dict]
    summary: str
    phase: str                         # "searching" | "awaiting_approval" | "summarizing" | "done"


# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a professional job-hunting assistant. Your mission is to find relevant job openings for the user based on their CV.

Given a CV, you will:
1. Extract key skills, experience level, job titles and technologies from the CV
2. Search for relevant job listings using multiple targeted queries (use at least 4-6 different searches)
3. Search on sites like: LinkedIn, Glassdoor, Indeed, JobMaster (דרושים), AllJobs, Drushim.co.il, and general Google searches
4. Collect diverse results from different sources

For each search, try variations like:
- "[Job title] jobs [location]"
- "[Main skill] developer jobs"
- "דרושים [תפקיד] [טכנולוגיה]" (Hebrew job sites)
- "[Technology stack] engineer hiring"

Return your findings as a structured list of job sources.
When you finish searching, respond with a JSON block like this:

```json
{
  "sources": [
    {
      "title": "Job title at Company",
      "url": "https://...",
      "snippet": "Brief description of the role",
      "company": "Company name",
      "location": "Tel Aviv / Remote / etc",
      "relevance_score": 9,
      "relevance_reason": "Why this matches the CV"
    }
  ]
}
```

Be thorough. The user is counting on you to find the best opportunities."""


# ── Agent class ───────────────────────────────────────────────────────────────

class JobHunterAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        self.search_tool = TavilySearch(
            max_results=5,
            api_key=os.getenv("TAVILY_API_KEY"),
        )
        self.tools = [self.search_tool]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.checkpointer = MemorySaver()
        self.graph = self._build_graph()
        self._pending_sources: list[dict] = []
        self._phase = "idle"

    def _build_graph(self) -> Any:
        tool_node = ToolNode(self.tools)

        def should_continue(state: AgentState):
            last = state["messages"][-1]
            if hasattr(last, "tool_calls") and last.tool_calls:
                return "tools"
            return "parse_results"

        def agent_node(state: AgentState):
            response = self.llm_with_tools.invoke(state["messages"])
            return {"messages": [response], "phase": "searching"}

        def parse_results_node(state: AgentState):
            """Extract structured sources from the agent's final message."""
            last_msg = state["messages"][-1]
            content = last_msg.content if hasattr(last_msg, "content") else ""

            sources = []
            # Try to extract JSON block
            if "```json" in content:
                try:
                    json_str = content.split("```json")[1].split("```")[0].strip()
                    data = json.loads(json_str)
                    sources = data.get("sources", [])
                except Exception:
                    pass

            # Fallback: try raw JSON
            if not sources:
                try:
                    data = json.loads(content)
                    sources = data.get("sources", [])
                except Exception:
                    pass

            # Last resort: scrape URLs from messages
            if not sources:
                sources = self._extract_sources_from_messages(state["messages"])

            return {
                "found_sources": sources,
                "phase": "awaiting_approval",
            }

        def summarize_node(state: AgentState):
            approved = state.get("approved_sources", [])
            if not approved:
                return {"summary": "לא נבחרו מקורות לסיכום.", "phase": "done"}

            sources_text = "\n".join(
                f"- {s.get('title','?')} at {s.get('company','?')} ({s.get('location','?')}): {s.get('snippet','')}"
                for s in approved
            )
            summary_prompt = f"""Based on the following approved job listings found for the candidate, write a concise Hebrew summary (3-5 sentences) that:
1. Describes the types of roles found
2. Highlights the best matches and why
3. Gives a general market impression

Job listings:
{sources_text}

Write the summary in Hebrew."""

            response = self.llm.invoke([HumanMessage(content=summary_prompt)])
            return {"summary": response.content, "phase": "done"}

        # Build graph
        builder = StateGraph(AgentState)
        builder.add_node("agent", agent_node)
        builder.add_node("tools", tool_node)
        builder.add_node("parse_results", parse_results_node)
        builder.add_node("summarize", summarize_node)

        builder.add_edge(START, "agent")
        builder.add_conditional_edges("agent", should_continue, {"tools": "tools", "parse_results": "parse_results"})
        builder.add_edge("tools", "agent")
        builder.add_edge("parse_results", END)
        builder.add_edge("summarize", END)

        return builder.compile(checkpointer=self.checkpointer)

    def _extract_sources_from_messages(self, messages: list) -> list[dict]:
        """Fallback: pull any tool result content into sources."""
        sources = []
        for msg in messages:
            if hasattr(msg, "content") and isinstance(msg.content, list):
                for block in msg.content:
                    if isinstance(block, dict) and block.get("type") == "tool_result":
                        sources.append({
                            "title": "Result",
                            "url": "",
                            "snippet": str(block.get("content", "")),
                            "company": "Unknown",
                            "location": "Unknown",
                            "relevance_score": 5,
                            "relevance_reason": "Found via search",
                        })
        return sources

    async def start(self, cv_text: str, thread_id: str) -> dict:
        """Kick off the agent with CV text."""
        config = {"configurable": {"thread_id": thread_id}}

        initial_state: AgentState = {
            "messages": [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=f"Here is the candidate's CV:\n\n{cv_text}\n\nPlease search for relevant job listings now."),
            ],
            "cv_text": cv_text,
            "found_sources": [],
            "approved_sources": [],
            "summary": "",
            "phase": "searching",
        }

        result = await self.graph.ainvoke(initial_state, config=config)

        self._phase = "awaiting_approval"
        sources = result.get("found_sources", [])
        self._pending_sources = sources

        return {
            "status": "awaiting_approval",
            "sources": sources,
            "message": f"מצאתי {len(sources)} מקורות רלוונטיים. אנא בחר את המקורות שברצונך לכלול:",
        }

    async def approve_sources(self, approved_indices: list[int], thread_id: str) -> dict:
        """User approved specific sources, now summarize."""
        config = {"configurable": {"thread_id": thread_id}}

        approved = [
            self._pending_sources[i]
            for i in approved_indices
            if 0 <= i < len(self._pending_sources)
        ]

        # Run summarize node directly
        state: AgentState = {
            "messages": [],
            "cv_text": "",
            "found_sources": self._pending_sources,
            "approved_sources": approved,
            "summary": "",
            "phase": "summarizing",
        }

        result = await self.graph.ainvoke(
            state,
            config={**config, "configurable": {"thread_id": thread_id + "_summary"}},
        )

        return {
            "status": "done",
            "approved_sources": approved,
            "summary": result.get("summary", ""),
        }

    def get_state(self) -> dict:
        return {"phase": self._phase, "pending_sources": self._pending_sources}
