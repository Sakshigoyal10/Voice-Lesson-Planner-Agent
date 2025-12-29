# NCERT Lesson Plan Generator (KVS)

Lightweight web app and MCP-enabled tool to generate NCERT-style lesson plans using voice or text input.

Key features
- Voice and text input for lesson creation
- Generates multi-session lesson plans, worksheets, and resources
- Export as DOCX and PDF
- Local SQLite database (default) to store transcripts and lessons
- MCP integration and a FastAPI router for programmatic access

Prerequisites
- Python 3.10+
- pip
- (Optional) Groq API key for higher-quality STT/LLM features

Install dependencies
```bash
pip install -r requirements.txt
```

Environment
- Create a `.env` file in the project root to set environment variables (optional):

```
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

Note: The project uses a local SQLite database file by default (`kvs_lessonplan.db`). No external DB is required to run locally.

Initialize database
%- The application will create the SQLite DB automatically when started, but you can view stats or reset using:

```bash
# Show stats
python setup_database.py --info

# Reset database (destructive)
python setup_database.py --reset
```

Run the application (development)
```bash
# Use uvicorn to serve the ASGI app (Socket.IO + FastAPI)
uvicorn main:socket_app --reload --host 0.0.0.0 --port 5000
```

Open the UI at: http://localhost:5000

MCP and API
- The FastAPI router for MCP tools is mounted at `/mcp` (see `mcp_integration.py`).
- There is an optional MCP server implementation in `mcp_server.py` which can be run separately.

Important files
- `main.py` — application entrypoint, Socket.IO and route handlers
- `templates/index_final.html` — frontend UI used by the app
- `database.py` — SQLAlchemy models and DB setup (defaults to SQLite)
- `crud.py` — database CRUD helpers
- `mcp_integration.py` — FastAPI MCP router and helper functions
- `mcp_server.py` — standalone MCP server (stdio-based)
- `setup_database.py` — helper script to inspect/reset DB

How to use (quick)
- Use the UI to switch between voice/text modes, provide topic/subject/class, then generate a lesson plan.
- Download generated lesson plans as DOCX or PDF from the UI.

Developer notes
- The default DB is SQLite for ease of local development. If you want PostgreSQL, update `database.py` to read `DATABASE_URL` from `.env` and create an engine accordingly.
- The Groq integration requires a valid `GROQ_API_KEY` to use Groq STT/LLM features.

Helpful commands
```bash
# Run the app
uvicorn main:socket_app --reload --port 5000

# Inspect DB (local SQLite)
sqlite3 kvs_lessonplan.db ".tables"

# Run MCP server (stdio)
python mcp_server.py
```

Notes on ports
- Default port used in docs: `5000`. Adjust as needed when launching with `uvicorn`.

Contributing
- Fork, create a feature branch, and open a pull request.

License
- MIT

Contact
- Create an issue in the repository for questions or bugs.

- MCP Protocol

---

**Happy Teaching! 🎉**
