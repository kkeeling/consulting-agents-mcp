# MCP Consulting Agents Development Guide

## Commands
- Start server: `./start_mcp_server.sh`
- Debug mode: `DEBUG=true ./start_mcp_server.sh`
- HTTP server: `MCP_TRANSPORT=http ./start_mcp_server.sh`
- Run tests: `python -m pytest tests/`
- Run single test: `python -m pytest tests/test_name.py::test_function`
- Lint: `python -m flake8 *.py`
- Type check: `python -m mypy *.py`

## API Testing (HTTP Mode)
- Test Sonny: `curl -X POST http://localhost:5000/consult -H "Content-Type: application/json" -d '{"agent":"Sonny","consultation_context":"Test message"}'`
- Test Darren: `curl -X POST http://localhost:5000/consult -H "Content-Type: application/json" -d '{"agent":"Darren","consultation_context":"Test message"}'`
- Test Sergey: `curl -X POST http://localhost:5000/consult -H "Content-Type: application/json" -d '{"agent":"Sergey","consultation_context":"Test message","search_query":"example search"}'`

## Environment Setup
- Python 3.8+ required
- Setup: `python -m venv mcp_venv && source mcp_venv/bin/activate && pip install -r requirements.txt`
- Configure `.env` file with `OPENAI_API_KEY` and `ANTHROPIC_API_KEY`

## Code Style Guidelines
- Follow PEP 8 standards for Python
- Line length: 88 characters (Black formatter compatible)
- Imports order: stdlib, third-party, local (separated by blank line)
- Use type hints for all functions and parameters
- Variable naming: snake_case for variables, UPPER_CASE for constants, PascalCase for classes
- Google-style docstrings with Args/Returns sections
- Structured logging with proper levels (info/error)
- Explicit exception handling with specific error messages
- Async functions for MCP tools, synchronous for internal functions