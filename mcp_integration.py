"""
MCP Integration with FastAPI
Complete implementation of Model Context Protocol with FastAPI
"""

import json
import asyncio
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal
import crud

# MCP Router
mcp_router = APIRouter(prefix="/mcp", tags=["MCP"])


class MCPToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]


class MCPToolResponse(BaseModel):
    success: bool
    data: Any
    error: Optional[str] = None


def get_db() -> Session:
    db = SessionLocal()
    try:
        return db
    finally:
        pass


def format_transcript(transcript) -> dict:
    return {
        "id": transcript.id,
        "text": transcript.transcript_text,
        "topic": transcript.detected_topic,
        "subject": transcript.detected_subject,
        "class": transcript.detected_class,
        "language": transcript.detected_language,
        "duration": transcript.audio_duration,
        "lesson_id": transcript.lesson_id,
        "created_at": transcript.created_at.isoformat() if transcript.created_at else None,
    }


def format_lesson_plan(lesson) -> dict:
    return {
        "lesson_id": lesson.lesson_id,
        "topic": lesson.topic,
        "subject": lesson.subject,
        "class_level": lesson.class_level,
        "language": lesson.language,
        "num_sessions": lesson.num_sessions,
        "session_duration": lesson.session_duration,
        "formatted_text": (lesson.formatted_text[:500] + "...")
        if lesson.formatted_text and len(lesson.formatted_text) > 500
        else lesson.formatted_text,
        "created_at": lesson.created_at.isoformat() if lesson.created_at else None,
    }


MCP_TOOLS = {
    "get_transcript": {
        "description": "Retrieve a transcript by ID",
        "parameters": {"transcript_id": {"type": "integer", "required": True}},
    },
    "search_transcripts": {
        "description": "Search transcripts by text content",
        "parameters": {
            "search_term": {"type": "string", "required": True},
            "limit": {"type": "integer", "required": False, "default": 10},
        },
    },
    "get_recent_transcripts": {
        "description": "Get most recent transcripts",
        "parameters": {"limit": {"type": "integer", "required": False, "default": 10}},
    },
    "get_lesson_plan": {
        "description": "Retrieve a lesson plan by ID",
        "parameters": {"lesson_id": {"type": "string", "required": True}},
    },
    "search_lesson_plans": {
        "description": "Search lesson plans by filters",
        "parameters": {
            "topic": {"type": "string", "required": False},
            "subject": {"type": "string", "required": False},
            "class_level": {"type": "string", "required": False},
            "limit": {"type": "integer", "required": False, "default": 10},
        },
    },
    "get_lesson_sessions": {
        "description": "Get all sessions for a lesson plan",
        "parameters": {"lesson_id": {"type": "string", "required": True}},
    },
    "get_statistics": {"description": "Get database statistics", "parameters": {}},
    "delete_lesson_plan": {
        "description": "Delete a lesson plan and its sessions",
        "parameters": {"lesson_id": {"type": "string", "required": True}},
    },
}


async def execute_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> MCPToolResponse:
    if tool_name not in MCP_TOOLS:
        return MCPToolResponse(success=False, data=None, error=f"Unknown tool: {tool_name}")

    db = get_db()
    try:
        if tool_name == "get_transcript":
            transcript_id = arguments.get("transcript_id")
            transcript = crud.get_transcript_by_id(db, transcript_id)
            if not transcript:
                return MCPToolResponse(success=False, data=None, error=f"Transcript {transcript_id} not found")
            return MCPToolResponse(success=True, data=format_transcript(transcript), error=None)

        elif tool_name == "search_transcripts":
            search_term = arguments.get("search_term")
            limit = arguments.get("limit", 10)
            transcripts = crud.search_transcripts(db, search_term, limit)
            results = [format_transcript(t) for t in transcripts]
            return MCPToolResponse(success=True, data={"count": len(results), "transcripts": results}, error=None)

        elif tool_name == "get_recent_transcripts":
            limit = arguments.get("limit", 10)
            transcripts = crud.get_recent_transcripts(db, limit)
            results = [format_transcript(t) for t in transcripts]
            return MCPToolResponse(success=True, data={"count": len(results), "transcripts": results}, error=None)

        elif tool_name == "get_lesson_plan":
            lesson_id = arguments.get("lesson_id")
            lesson = crud.get_lesson_plan_by_id(db, lesson_id)
            if not lesson:
                return MCPToolResponse(success=False, data=None, error=f"Lesson plan {lesson_id} not found")
            return MCPToolResponse(success=True, data=format_lesson_plan(lesson), error=None)

        elif tool_name == "search_lesson_plans":
            topic = arguments.get("topic")
            subject = arguments.get("subject")
            class_level = arguments.get("class_level")
            limit = arguments.get("limit", 10)
            lessons = crud.search_lesson_plans(db, topic, subject, class_level, limit)
            results = [format_lesson_plan(l) for l in lessons]
            return MCPToolResponse(success=True, data={"count": len(results), "lesson_plans": results}, error=None)

        elif tool_name == "get_lesson_sessions":
            lesson_id = arguments.get("lesson_id")
            sessions = crud.get_sessions_by_lesson_id(db, lesson_id)
            results = []
            for session in sessions:
                results.append(
                    {
                        "session_number": session.session_number,
                        "duration": session.duration,
                        "competency": session.competency,
                        "elo": session.elo,
                        "activities": json.loads(session.activities) if session.activities else [],
                        "resources": session.resources_tlm,
                        "worksheets": session.worksheets,
                        "assessment": session.assessment,
                    }
                )
            return MCPToolResponse(
                success=True,
                data={"lesson_id": lesson_id, "total_sessions": len(results), "sessions": results},
                error=None,
            )

        elif tool_name == "get_statistics":
            stats = crud.get_statistics(db)
            return MCPToolResponse(success=True, data=stats, error=None)

        elif tool_name == "delete_lesson_plan":
            lesson_id = arguments.get("lesson_id")
            success = crud.delete_lesson_plan(db, lesson_id)
            return MCPToolResponse(
                success=success,
                data={"message": f"Lesson plan {lesson_id} deleted" if success else "Lesson plan not found"},
                error=None if success else "Deletion failed",
            )

        return MCPToolResponse(success=False, data=None, error=f"Tool implementation missing: {tool_name}")

    except Exception as e:
        return MCPToolResponse(success=False, data=None, error=str(e))

    finally:
        db.close()


@mcp_router.get("/tools")
async def list_mcp_tools():
    return {
        "success": True,
        "tools": [
            {"name": name, "description": info["description"], "parameters": info["parameters"]}
            for name, info in MCP_TOOLS.items()
        ],
    }


@mcp_router.post("/execute")
async def execute_tool(tool_call: MCPToolCall):
    response = await execute_mcp_tool(tool_call.name, tool_call.arguments)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)
    return response


@mcp_router.get("/statistics")
async def get_mcp_statistics():
    response = await execute_mcp_tool("get_statistics", {})
    return response


@mcp_router.get("/lessons/recent")
async def get_recent_lessons_mcp(limit: int = 10):
    db = get_db()
    try:
        lessons = crud.get_recent_lesson_plans(db, limit=limit)
        return {"success": True, "data": {"count": len(lessons), "lessons": [format_lesson_plan(l) for l in lessons]}}
    finally:
        db.close()


@mcp_router.get("/transcripts/recent")
async def get_recent_transcripts_mcp(limit: int = 10):
    db = get_db()
    try:
        transcripts = crud.get_recent_transcripts(db, limit=limit)
        return {"success": True, "data": {"count": len(transcripts), "transcripts": [format_transcript(t) for t in transcripts]}}
    finally:
        db.close()


class MCPContext:
    def __init__(self):
        self.tools = MCP_TOOLS

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        response = await execute_mcp_tool(name, arguments)
        return {"success": response.success, "data": response.data, "error": response.error}

    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {"name": name, "description": info["description"], "parameters": info["parameters"]}
            for name, info in self.tools.items()
        ]


mcp_context = MCPContext()

__all__ = ["mcp_router", "mcp_context", "execute_mcp_tool", "MCPToolCall", "MCPToolResponse"]
