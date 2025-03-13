# MCP Consulting Agents Development Guide

## Commands
- Start server: `./start_mcp_server.sh`
- Debug mode: `DEBUG=true ./start_mcp_server.sh`
- Test Sonny: `curl -X POST http://localhost:5000/consult -H "Content-Type: application/json" -d '{"agent":"Sonny","consultation_context":"Test message"}'`
- Test Darren: `curl -X POST http://localhost:5000/consult -H "Content-Type: application/json" -d '{"agent":"Darren","consultation_context":"Test message"}'`
- Test Sergey: `curl -X POST http://localhost:5000/consult -H "Content-Type: application/json" -d '{"agent":"Sergey","consultation_context":"Test message","search_query":"example search"}'`

## Environment Setup
- Python 3.8+ required
- Setup: `python -m venv mcp_venv && source mcp_venv/bin/activate`
- Configure `.env` file with `OPENAI_API_KEY` and `ANTHROPIC_API_KEY`

## Agent Capabilities
- Darren (OpenAI o3-mini): Expert code consultant with high reasoning
- Sonny (Claude 3.7 Sonnet): Code consultant with extended thinking
- Sergey (GPT-4o): Web search specialist for finding documentation and examples

## Code Style Guidelines
- Follow PEP 8 standards for Python
- Use type hints for all functions (from typing import Any, Dict, List, Optional)
- Imports organized: standard library, third-party, local modules
- Google-style docstrings for all functions and classes
- Use structured logging for consistency
- Error handling with specific exception messages
- Variable naming: snake_case for variables, UPPER_CASE for constants
- Maximum line length of 88 characters (Black formatter compatible)