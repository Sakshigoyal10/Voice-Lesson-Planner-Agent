"""
MCP Server for KVS Lesson Plan Generator
Provides tools for transcript and lesson plan management
"""

from typing import Any, Optional, List
from mcp.server import Server
from mcp.types import Tool, TextContent, Resource
import json
from sqlalchemy.orm import Session
from database import SessionLocal
import crud

# Initialize MCP Server
mcp_server = Server("kvs-lessonplan-mcp")


def get_db() -> Session:
    """Get database session"""
    return SessionLocal()


def format_transcript(transcript) -> dict:
    """Format transcript object for response"""
    return {
        "id": transcript.id,
        "text": transcript.transcript_text,
        "topic": transcript.detected_topic,
        "subject": transcript.detected_subject,
        "class": transcript.detected_class,
        "language": transcript.detected_language,
        "duration": transcript.audio_duration,
        "lesson_id": transcript.lesson_id,
        "created_at": transcript.created_at.isoformat() if transcript.created_at else None
    }


def format_lesson_plan(lesson) -> dict:
    """Format lesson plan object for response"""
    return {
        "lesson_id": lesson.lesson_id,
        "topic": lesson.topic,
        "subject": lesson.subject,
        "class_level": lesson.class_level,
        "language": lesson.language,
        "num_sessions": lesson.num_sessions,
        "session_duration": lesson.session_duration,
        "created_at": lesson.created_at.isoformat() if lesson.created_at else None,
        "updated_at": lesson.updated_at.isoformat() if lesson.updated_at else None
    }


@mcp_server.list_tools()
async def list_tools() -> List[Tool]:
    """List all available MCP tools"""
    return [
        Tool(
            name="get_transcript",
            description="Retrieve a transcript by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "transcript_id": {"type": "integer", "description": "The transcript ID"},
                },
                "required": ["transcript_id"]
            },
        ),
        Tool(
            name="search_transcripts",
            description="Search transcripts by text content",
            inputSchema={
                "type": "object",
                "properties": {
                    "search_term": {"type": "string", "description": "Text to search for in transcripts"},
                    "limit": {"type": "integer", "description": "Maximum number of results", "default": 10},
                },
                "required": ["search_term"]
            },
        ),
        Tool(
            name="get_recent_transcripts",
            description="Get most recent transcripts",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Number of transcripts to retrieve", "default": 10},
                }
            },
        ),
        Tool(
            name="get_lesson_plan",
            description="Retrieve a lesson plan by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "lesson_id": {"type": "string", "description": "The lesson plan ID"},
                },
                "required": ["lesson_id"]
            },
        ),
        Tool(
            name="search_lesson_plans",
            description="Search lesson plans by topic, subject, or class",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Topic to search for"},
                    "subject": {"type": "string", "description": "Subject filter (e.g., Mathematics, Science)"},
                    "class_level": {"type": "string", "description": "Class level filter (e.g., Class 1, Class 2)"},
                    "limit": {"type": "integer", "description": "Maximum number of results", "default": 10},
                }
            },
        ),
        Tool(
            name="get_lesson_sessions",
            description="Get all sessions for a lesson plan",
            inputSchema={
                "type": "object",
                "properties": {
                    "lesson_id": {"type": "string", "description": "The lesson plan ID"},
                },
                "required": ["lesson_id"]
            },
        ),
        Tool(
            name="get_statistics",
            description="Get database statistics (total transcripts, lessons, etc.)",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="delete_lesson_plan",
            description="Delete a lesson plan and its sessions",
            inputSchema={
                "type": "object",
                "properties": {
                    "lesson_id": {"type": "string", "description": "The lesson plan ID to delete"},
                },
                "required": ["lesson_id"]
            },
        ),
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    """Handle tool calls"""
    db = get_db()
    try:
        # Transcript tools
        if name == "get_transcript":
            transcript_id = arguments.get("transcript_id")
            transcript = crud.get_transcript_by_id(db, transcript_id)
            if not transcript:
                return [TextContent(type="text", text=json.dumps({"error": f"Transcript {transcript_id} not found"}))]
            return [TextContent(type="text", text=json.dumps(format_transcript(transcript), indent=2))]

        elif name == "search_transcripts":
            search_term = arguments.get("search_term")
            limit = arguments.get("limit", 10)
            transcripts = crud.search_transcripts(db, search_term, limit)
            results = [format_transcript(t) for t in transcripts]
            return [TextContent(type="text", text=json.dumps({"count": len(results), "transcripts": results}, indent=2))]

        elif name == "get_recent_transcripts":
            limit = arguments.get("limit", 10)
            transcripts = crud.get_recent_transcripts(db, limit)
            results = [format_transcript(t) for t in transcripts]
            return [TextContent(type="text", text=json.dumps({"count": len(results), "transcripts": results}, indent=2))]

        # Lesson plan tools
        elif name == "get_lesson_plan":
            lesson_id = arguments.get("lesson_id")
            lesson = crud.get_lesson_plan_by_id(db, lesson_id)
            if not lesson:
                return [TextContent(type="text", text=json.dumps({"error": f"Lesson plan {lesson_id} not found"}))]
            return [TextContent(type="text", text=json.dumps(format_lesson_plan(lesson), indent=2))]

        elif name == "search_lesson_plans":
            topic = arguments.get("topic")
            subject = arguments.get("subject")
            class_level = arguments.get("class_level")
            limit = arguments.get("limit", 10)
            lessons = crud.search_lesson_plans(db, topic, subject, class_level, limit)
            results = [format_lesson_plan(l) for l in lessons]
            return [TextContent(type="text", text=json.dumps({"count": len(results), "lesson_plans": results}, indent=2))]

        elif name == "get_lesson_sessions":
            lesson_id = arguments.get("lesson_id")
            sessions = crud.get_sessions_by_lesson_id(db, lesson_id)
            results = []
            for session in sessions:
                results.append({
                    "session_number": session.session_number,
                    "duration": session.duration,
                    "competency": session.competency,
                    "elo": session.elo,
                    "activities": json.loads(session.activities) if session.activities else [],
                    "resources": session.resources_tlm,
                    "worksheets": session.worksheets,
                    "assessment": session.assessment
                })
            return [TextContent(type="text", text=json.dumps({"lesson_id": lesson_id, "total_sessions": len(results), "sessions": results}, indent=2))]

        elif name == "get_statistics":
            stats = crud.get_statistics(db)
            return [TextContent(type="text", text=json.dumps(stats, indent=2))]

        elif name == "delete_lesson_plan":
            lesson_id = arguments.get("lesson_id")
            success = crud.delete_lesson_plan(db, lesson_id)
            return [TextContent(type="text", text=json.dumps({
                "success": success,
                "message": f"Lesson plan {lesson_id} deleted" if success else "Lesson plan not found"
            }))]

        else:
            return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

    finally:
        db.close()


@mcp_server.list_resources()
async def list_resources() -> List[Resource]:
    """List available resources"""
    return [
        Resource(
            uri="kvs://statistics",
            name="Database Statistics",
            mimeType="application/json",
            description="Overall database statistics and metrics",
        ),
        Resource(
            uri="kvs://recent-lessons",
            name="Recent Lesson Plans",
            mimeType="application/json",
            description="10 most recent lesson plans",
        ),
        Resource(
            uri="kvs://recent-transcripts",
            name="Recent Transcripts",
            mimeType="application/json",
            description="10 most recent voice transcripts",
        ),
    ]


@mcp_server.read_resource()
async def read_resource(uri: str) -> str:
    """Read resource content"""
    db = get_db()
    try:
        if uri == "kvs://statistics":
            stats = crud.get_statistics(db)
            return json.dumps(stats, indent=2)

        elif uri == "kvs://recent-lessons":
            lessons = crud.get_recent_lesson_plans(db, limit=10)
            results = [format_lesson_plan(l) for l in lessons]
            return json.dumps({"lessons": results}, indent=2)

        elif uri == "kvs://recent-transcripts":
            transcripts = crud.get_recent_transcripts(db, limit=10)
            results = [format_transcript(t) for t in transcripts]
            return json.dumps({"transcripts": results}, indent=2)

        else:
            return json.dumps({"error": f"Unknown resource: {uri}"})

    finally:
        db.close()


async def main():
    """Run MCP server"""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(read_stream, write_stream, mcp_server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
