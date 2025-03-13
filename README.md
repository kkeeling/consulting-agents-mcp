# ConsultingAgents MCP Server

A Model Context Protocol (MCP) server that allows Claude Code to consult with additional AI agents for code and problem analysis. This server provides access to Darren (OpenAI) and Sonny (Anthropic) as expert coding consultants, enabling multi-model perspective on coding problems.

## Features

- **Darren**: OpenAI expert coding consultant powered by o3-mini model with high reasoning capabilities
- **Sonny**: Anthropic expert coding consultant powered by Claude 3.7 Sonnet with enhanced thinking
- **MCP Integration**: Seamless integration with Claude Code via MCP protocol
- **Multiple Transport Options**: Supports stdio (for direct Claude Code integration) and HTTP/SSE transport

## Prerequisites

- Python 3.8+
- OpenAI API key
- Anthropic API key
- Claude Code CLI (for integration)

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/consulting-agents-mcp.git
   cd consulting-agents-mcp
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv mcp_venv
   source mcp_venv/bin/activate  # On Windows: mcp_venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up API keys**:
   Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

5. **Start the server**:
   ```bash
   chmod +x start_mcp_server.sh
   ./start_mcp_server.sh
   ```

## Integration with Claude Code

1. **Register the MCP server** with Claude Code:
   ```bash
   claude mcp add ConsultingAgents /absolute/path/to/consulting-agents-mcp/start_mcp_server.sh
   ```

2. **Start Claude Code** with MCP integration:
   ```bash
   claude --mcp-debug
   ```

3. **Use the tools** in Claude Code:
   ```
   Now you can use consult_with_darren and consult_with_sonny functions in Claude Code.
   ```

## Available Tools

The MCP server provides two consulting tools:

### `consult_with_darren`
Uses OpenAI's o3-mini model with high reasoning to analyze code and provide recommendations.

Parameters:
- `consultation_context`: Description of the problem (required)
- `source_code`: Optional code to analyze

### `consult_with_sonny`
Uses Claude 3.7 Sonnet with enhanced thinking to provide in-depth code analysis.

Parameters:
- `consultation_context`: Description of the problem (required)
- `source_code`: Optional code to analyze

## Advanced Configuration

### Environment Variables

- `MCP_TRANSPORT`: Transport protocol (default: "stdio", alternatives: "http", "sse")
- `HOST`: Server host when using HTTP/SSE transport (default: "127.0.0.1")
- `PORT`: Server port when using HTTP/SSE transport (default: 5000)

### HTTP API (When Using HTTP Transport)

When running with HTTP transport, the server provides these endpoints:

#### Health Check
```
GET /health
```

Returns server status and available agents.

#### Model Consultation
```
POST /consult
```

Request body:
```json
{
  "agent": "Darren",
  "consultation_context": "I have a bug in my code where...",
  "source_code": "def example():\n    return 'hello'"
}
```

## Troubleshooting

- **MCP Server Not Found**: Verify the absolute path in your claude mcp add command
- **API Authentication Errors**: Check that your API keys are correctly set in the .env file
- **Connection Issues**: Ensure the MCP server is running before starting Claude Code
- **Debug Logs**: Check the terminal where the MCP server is running for detailed logs

## Development

### Running in Development Mode

1. Start the server with debug output:
   ```bash
   DEBUG=true ./start_mcp_server.sh
   ```

2. Test HTTP endpoints (when using HTTP transport):
   ```bash
   curl -X POST http://localhost:5000/consult \
     -H "Content-Type: application/json" \
     -d '{"agent":"Sonny","consultation_context":"Test message"}'
   ```

### Project Structure

- `mcp_consul_server.py`: Main MCP server implementation
- `start_mcp_server.sh`: Script to start the server with proper environment
- `requirements.txt`: Python dependencies

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.