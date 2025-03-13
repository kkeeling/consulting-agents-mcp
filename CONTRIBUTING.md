# Contributing to ConsultingAgents MCP

Thank you for considering contributing to the ConsultingAgents MCP server! This document provides guidelines for contributions.

## Ways to Contribute

- Reporting bugs and issues
- Suggesting enhancements
- Improving documentation
- Adding new features
- Refactoring code

## Getting Started

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests if applicable
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Pull Request Guidelines

- Update documentation if needed
- Keep pull requests focused on a single topic
- Add tests if applicable
- Follow the existing code style
- Write clear commit messages

## Development Setup

1. Clone the repository
2. Create a virtual environment
   ```bash
   python -m venv mcp_venv
   source mcp_venv/bin/activate
   ```
3. Install development dependencies
   ```bash
   pip install -r requirements.txt
   ```
4. Create a .env file with your API keys
   ```
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   ```

## Code Style

- Follow PEP 8 guidelines
- Use type hints where applicable
- Add docstrings to new functions and classes

## Questions?

If you have any questions, feel free to open an issue for discussion.

Thank you for your contributions!