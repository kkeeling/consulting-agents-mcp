import os
import sys
import logging
import requests
import json
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load API keys from .env file
load_dotenv()

# Check for required API keys
if not os.getenv("OPENAI_API_KEY"):
    logger.error("OPENAI_API_KEY is not set in environment or .env file")
if not os.getenv("ANTHROPIC_API_KEY"):
    logger.error("ANTHROPIC_API_KEY is not set in environment or .env file")

# Initialize MCP server
mcp = FastMCP("ConsultingAgent")

# Constants for consulting agents
DARREN_MODEL = "o3-mini"  # Darren uses base o3-mini model.
OPENAI_URL = "https://api.openai.com/v1/responses"  # New endpoint

SONNY_MODEL = "claude-3-7-sonnet-20250219"
SONNY_THINKING_BUDGET = 16000
SONNY_MAX_TOKENS = 32000
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"  # Consider using a more recent version if needed

def verify_api_keys() -> None:
    """Verify API keys are available"""
    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY is not set")
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise EnvironmentError("ANTHROPIC_API_KEY is not set")

def consult_darren(prompt: str) -> str:
    """
    Consult with Darren using OpenAI's responses API with o3-mini and high reasoning.
    """
    verify_api_keys()
    system_message = "You are an expert coding and debugging consultant. You think deeply and carefully about questions. You look at problems from all angles. Provide a comprehensive analysis."
    
    # Format using the new responses API format
    payload = {
        "model": DARREN_MODEL,
        "input": prompt,
        "instructions": system_message,
        "reasoning": {
            "effort": "high"  # Use high reasoning for detailed analysis
        }
    }
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        "Content-Type": "application/json"
    }
    
    logger.info(f"Consulting Darren with {len(prompt)} character prompt")
    try:
        response = requests.post(OPENAI_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"OpenAI API request failed: {str(e)}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"Response: {e.response.text}")
        raise Exception(f"OpenAI API request failed: {str(e)}")
        
    try:
        data = response.json()
        # Parse the response according to the new format
        for output_item in data.get("output", []):
            if output_item.get("type") == "message" and output_item.get("role") == "assistant":
                for content_item in output_item.get("content", []):
                    if content_item.get("type") == "output_text":
                        answer = content_item.get("text", "")
                        logger.info(f"Darren responded with {len(answer)} character response")
                        return answer
        
        # If we couldn't find the output in the expected format, try SDK convenience property
        if "output_text" in data:
            answer = data["output_text"]
            logger.info(f"Darren responded with {len(answer)} character response (from output_text)")
            return answer
            
        # If we still can't find the response, raise an exception
        logger.error(f"Unexpected OpenAI response format: {data.keys()}")
        logger.error(f"Response content: {json.dumps(data)[:500]}...")
        raise Exception("Could not parse response from OpenAI API")
    except (KeyError, IndexError, ValueError) as e:
        logger.error(f"Failed to parse OpenAI response: {str(e)}")
        logger.error(f"Response content: {response.text[:500]}...")
        raise Exception(f"Unexpected OpenAI API response format: {str(e)}")

def consult_sonny(prompt: str) -> str:
    """
    Consult with Sonny using the Anthropic API with extended thinking enabled.
    """
    verify_api_keys()
    payload = {
        "model": SONNY_MODEL,
        "max_tokens": SONNY_MAX_TOKENS,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "thinking": {"type": "enabled", "budget_tokens": SONNY_THINKING_BUDGET}
    }
    headers = {
        "x-api-key": os.getenv("ANTHROPIC_API_KEY"),
        "anthropic-version": ANTHROPIC_VERSION,
        "Content-Type": "application/json"
    }
    
    logger.info(f"Consulting Sonny with {len(prompt)} character prompt")
    try:
        response = requests.post(ANTHROPIC_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Anthropic API request failed: {str(e)}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"Response: {e.response.text}")
        raise Exception(f"Anthropic API request failed: {str(e)}")
    
    try:
        data = response.json()
        # Handle Anthropic's content format
        if "content" in data:
            reply = ""
            for block in data.get("content", []):
                if block.get("type") == "text":
                    reply = block.get("text", "")
                    break
                    
            if reply:
                logger.info(f"Sonny responded with {len(reply)} character response")
                return reply
        
        # Alternative parsing if needed
        if "content" not in data and "completion" in data:
            logger.info("Using legacy response format")
            reply = data.get("completion", "")
            if reply:
                return reply
                
        logger.error(f"Unexpected Anthropic response format: {data.keys()}")
        raise Exception("No text reply found in Anthropic API response.")
    except Exception as e:
        logger.error(f"Failed to parse Anthropic response: {str(e)}")
        logger.error(f"Response content: {response.text[:500]}...")
        raise Exception(f"Failed to parse Anthropic response: {str(e)}")

@mcp.tool()
async def consult_with_darren(consultation_context: str, source_code: Optional[str] = None) -> str:
    """Consult with Darren (OpenAI o3-mini) about a coding problem.
    
    Args:
        consultation_context: Description of the problem or question you have
        source_code: Optional source code to analyze
        
    Returns:
        Darren's analysis and recommendations
    """
    prompt = f"{consultation_context}\n\n"
    if source_code:
        prompt += f"Source Code:\n{source_code}\n\n"
    prompt += "Please provide a thorough analysis and any recommendations."
    
    logger.info("Processing consultation request for Darren")
    try:
        result = consult_darren(prompt)
        return result
    except Exception as e:
        logger.error(f"Error consulting with Darren: {str(e)}")
        return f"Error consulting with Darren: {str(e)}"

@mcp.tool()
async def consult_with_sonny(consultation_context: str, source_code: Optional[str] = None) -> str:
    """Consult with Sonny (Claude 3.7 Sonnet) about a coding problem.
    
    Args:
        consultation_context: Description of the problem or question you have
        source_code: Optional source code to analyze
        
    Returns:
        Sonny's analysis and recommendations
    """
    prompt = f"{consultation_context}\n\n"
    if source_code:
        prompt += f"Source Code:\n{source_code}\n\n"
    prompt += "Please provide a thorough analysis and any recommendations."
    
    logger.info("Processing consultation request for Sonny")
    try:
        result = consult_sonny(prompt)
        return result
    except Exception as e:
        logger.error(f"Error consulting with Sonny: {str(e)}")
        return f"Error consulting with Sonny: {str(e)}"

if __name__ == "__main__":
    # Get transport from environment or default to stdio
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    
    # Only set these if using http transport
    if transport == "http" or transport == "sse":
        port = int(os.environ.get("PORT", 5000))
        host = os.environ.get("HOST", "127.0.0.1")
        os.environ["FASTMCP_HOST"] = host
        os.environ["FASTMCP_PORT"] = str(port)
        print(f"Starting MCP Consultation Server on {host}:{port} with {transport} transport")
    else:
        print(f"Starting MCP Consultation Server with {transport} transport")
    
    # Check API keys at startup but don't stop server
    if not os.getenv("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY is not set. Darren agent won't work.")
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("WARNING: ANTHROPIC_API_KEY is not set. Sonny agent won't work.")
    
    # Run the MCP server with appropriate transport
    mcp.run(transport=transport)