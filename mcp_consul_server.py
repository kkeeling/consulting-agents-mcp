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
if not os.getenv("GOOGLE_API_KEY"):
    logger.error("GOOGLE_API_KEY is not set in environment or .env file")

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

SERGEY_MODEL = "gpt-4o"  # Sergey uses gpt-4o with web search capabilities
SERGEY_SEARCH_CONTEXT_SIZE = "high"  # Maximum search context for comprehensive results

GEMMA_MODEL = "gemini-2.5-pro-exp-0325"  # Gemma uses Gemini model with extended context
GEMMA_MAX_TOKENS = 1000000  # Massive 1M token context window for repository analysis
GOOGLE_AI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"  # Gemini API endpoint

def verify_api_keys() -> None:
    """Verify API keys are available"""
    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY is not set")
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise EnvironmentError("ANTHROPIC_API_KEY is not set")
    if not os.getenv("GOOGLE_API_KEY"):
        raise EnvironmentError("GOOGLE_API_KEY is not set")

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

def consult_sergey(prompt: str, search_query: Optional[str] = None) -> str:
    """
    Consult with Sergey using OpenAI's Responses API with GPT-4o and web search.
    
    Args:
        prompt: The prompt to send to the model
        search_query: Optional specific search query to use
    """
    verify_api_keys()
    
    # Prepare tools array with web search
    tools = [{
        "type": "web_search_preview",
        "search_context_size": SERGEY_SEARCH_CONTEXT_SIZE
    }]
    
    system_message = "You are Sergey, an expert at web search who helps find relevant API documentation and information for coding projects. When answering, include relevant citations to sources."
    
    # Format payload for the Responses API with web search
    payload = {
        "model": SERGEY_MODEL,
        "input": prompt,
        "instructions": system_message,
        "tools": tools
    }
    
    # Add specific search query to instructions if provided
    if search_query:
        payload["instructions"] += f"\n\nPlease specifically search for: {search_query}"
    
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        "Content-Type": "application/json"
    }
    
    logger.info(f"Consulting Sergey with {len(prompt)} character prompt")
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
        
        # Process the response to extract the content and any citations
        answer = ""
        # Process output array like in consult_darren function
        for output_item in data.get("output", []):
            if output_item.get("type") == "message" and output_item.get("role") == "assistant":
                for content_item in output_item.get("content", []):
                    if content_item.get("type") == "output_text":
                        answer = content_item.get("text", "")
                        # We could also extract annotations/citations here if needed
                        
                        logger.info(f"Sergey responded with {len(answer)} character response")
                        return answer
        
        # Fallback if we couldn't find the response in the expected format
        if "output_text" in data:
            answer = data["output_text"]
            logger.info(f"Sergey responded with {len(answer)} character response (from output_text)")
            return answer
            
        logger.error(f"Unexpected OpenAI response format: {data.keys()}")
        logger.error(f"Response content: {json.dumps(data)[:500]}...")
        raise Exception("Could not parse response from OpenAI API")
    except (KeyError, IndexError, ValueError) as e:
        logger.error(f"Failed to parse OpenAI response: {str(e)}")
        logger.error(f"Response content: {response.text[:500]}...")
        raise Exception(f"Unexpected OpenAI API response format: {str(e)}")

def consult_gemma(prompt: str, repo_url: str) -> str:
    """
    Consult with Gemma using Google's Gemini API with the repository analysis capabilities.
    
    Args:
        prompt: The prompt to send to the model
        repo_url: The GitHub repository URL to analyze
    """
    verify_api_keys()
    
    # Construct the URL for the API request
    api_url = GOOGLE_AI_URL.format(model=GEMMA_MODEL)
    
    # Add API key as a query parameter
    api_url = f"{api_url}?key={os.getenv('GOOGLE_API_KEY')}"
    
    # Instructions for using GitIngest
    git_ingest_instructions = f"""
    Use the https://github.com/cyclotruc/gitingest tool to create a comprehensive text version of the 
    repository at {repo_url}. This will allow you to analyze the entire codebase within your 1M token context window.
    """
    
    # Thinking structure based on Google's API documentation
    thinking_instructions = """
    When analyzing this request, use the following structure:
    1. Parse the feature/task requirements carefully
    2. Understand the repository structure
    3. Identify relevant components that will need modification
    4. Determine dependencies between components
    5. Formulate a comprehensive plan that includes:
       - Files that need to be modified
       - New files that need to be created
       - Tests that need to be updated or added
       - Documentation changes required
    """
    
    # Format the system message
    system_message = f"""You are Gemma, an expert at codebase analysis who specializes in reviewing entire code repositories to provide comprehensive development plans. 
    
    {git_ingest_instructions}
    
    {thinking_instructions}
    
    When responding, provide a structured plan that includes:
    1. Component analysis - which parts of the code need to be modified
    2. Dependency list - what other components will be affected
    3. Testing plan - how the changes should be tested
    4. Documentation plan - what documentation needs to be updated
    
    Always cite specific files and code structures in your analysis."""
    
    # Format the payload according to Gemini API specs
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": system_message + "\n\n" + prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "topP": 0.8,
            "topK": 40,
            "maxOutputTokens": 8192
        },
        "safetySettings": [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    logger.info(f"Consulting Gemma with {len(prompt)} character prompt for repository: {repo_url}")
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Google AI API request failed: {str(e)}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"Response: {e.response.text}")
        raise Exception(f"Google AI API request failed: {str(e)}")
    
    try:
        data = response.json()
        
        # Parse the Gemini API response format
        if "candidates" in data and len(data["candidates"]) > 0:
            candidate = data["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                for part in candidate["content"]["parts"]:
                    if "text" in part:
                        answer = part["text"]
                        logger.info(f"Gemma responded with {len(answer)} character response")
                        return answer
        
        logger.error(f"Unexpected Google AI response format: {json.dumps(data)[:500]}...")
        raise Exception("Could not parse response from Google AI API")
    except (KeyError, IndexError, ValueError) as e:
        logger.error(f"Failed to parse Google AI response: {str(e)}")
        logger.error(f"Response content: {response.text[:500]}...")
        raise Exception(f"Unexpected Google AI API response format: {str(e)}")

@mcp.tool()
async def consult_with_darren(consultation_context: str, source_code: Optional[str] = None) -> str:
    """Consult with Darren (OpenAI o3-mini) about a coding problem.
    
    Args:
        consultation_context: Description of the problem or question you have
        source_code: Optional source code to analyze
        
    Returns:
        Darren's analysis and recommendations
    """
    prompt = "You are a software development expert who excels at examining tasks deeply and thoroughly. You strive to provide expert advice, including context, solutions, and examples.\n\n"
    prompt += f"<context>\n{consultation_context}\n</context>\n\n"
    
    if source_code:
        # Handle source code formatting
        if "<project_structure>" in source_code or "<" in source_code and ".py>" in source_code:
            # Source code is already formatted with our special tags
            prompt += source_code
        else:
            # Legacy format - just add the source code as is
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
    prompt = "You are a software development expert who excels at examining tasks deeply and thoroughly. You strive to provide expert advice, including context, solutions, and examples.\n\n"
    prompt += f"<context>\n{consultation_context}\n</context>\n\n"
    
    if source_code:
        # Handle source code formatting
        if "<project_structure>" in source_code or "<" in source_code and ".py>" in source_code:
            # Source code is already formatted with our special tags
            prompt += source_code
        else:
            # Legacy format - just add the source code as is
            prompt += f"Source Code:\n{source_code}\n\n"
    
    prompt += "Please provide a thorough analysis and any recommendations."
    
    logger.info("Processing consultation request for Sonny")
    try:
        result = consult_sonny(prompt)
        return result
    except Exception as e:
        logger.error(f"Error consulting with Sonny: {str(e)}")
        return f"Error consulting with Sonny: {str(e)}"

@mcp.tool()
async def consult_with_sergey(consultation_context: str, search_query: Optional[str] = None, source_code: Optional[str] = None) -> str:
    """Consult with Sergey (GPT-4o with web search) to find relevant documentation and information.
    
    Args:
        consultation_context: Description of what information or documentation you need
        search_query: Optional specific search query to use
        source_code: Optional source code for context
        
    Returns:
        Sergey's findings with citations to relevant documentation
    """
    # Get current date for Sergey to prioritize recent content
    from datetime import datetime
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    prompt = f"You are a software development expert who excels at web search and finding relevant documentation. You strive to provide expert advice with citations, solutions, and examples. Today's date is {current_date}. Please prioritize content that is as recent as possible, and always prefer official documentation and primary sources over third-party blogs or tutorials.\n\n"
    prompt += f"<context>\n{consultation_context}\n</context>\n\n"
    
    if source_code:
        # Handle source code formatting
        if "<project_structure>" in source_code or "<" in source_code and ".py>" in source_code:
            # Source code is already formatted with our special tags
            prompt += source_code
        else:
            # Legacy format - just add the source code as is
            prompt += f"Source Code:\n{source_code}\n\n"
    
    prompt += "Please provide relevant information, documentation, and examples with citations to sources."
    
    logger.info("Processing consultation request for Sergey")
    try:
        result = consult_sergey(prompt, search_query)
        return result
    except Exception as e:
        logger.error(f"Error consulting with Sergey: {str(e)}")
        return f"Error consulting with Sergey: {str(e)}"

@mcp.tool()
async def consult_with_gemma(consultation_context: str, repo_url: str, feature_description: str) -> str:
    """Consult with Gemma (Gemini 2.5 Pro) to analyze entire repositories and provide comprehensive development plans.
    
    Args:
        consultation_context: Description of the task or feature to be implemented
        repo_url: The GitHub repository URL to analyze
        feature_description: Detailed description of the feature to be implemented
        
    Returns:
        Gemma's comprehensive plan including component analysis, dependencies, testing, and documentation
    """
    prompt = f"""Claude Code is working on implementing the following feature:

<task>
{consultation_context}
</task>

<feature_details>
{feature_description}
</feature_details>

Analyze the entire repository to create a comprehensive implementation plan. Focus on:

1. Identifying all components that need modification
2. Finding any redundant code that could be consolidated
3. Mapping dependencies between components
4. Creating a testing strategy
5. Planning documentation updates

Provide a structured response organized by:
- Component Analysis
- Implementation Steps
- Dependencies
- Testing Plan
- Documentation Requirements
"""
    
    logger.info(f"Processing repository analysis request for Gemma: {repo_url}")
    try:
        result = consult_gemma(prompt, repo_url)
        return result
    except Exception as e:
        logger.error(f"Error consulting with Gemma: {str(e)}")
        return f"Error consulting with Gemma: {str(e)}"

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
        print("WARNING: OPENAI_API_KEY is not set. Darren and Sergey agents won't work.")
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("WARNING: ANTHROPIC_API_KEY is not set. Sonny agent won't work.")
    if not os.getenv("GOOGLE_API_KEY"):
        print("WARNING: GOOGLE_API_KEY is not set. Gemma agent won't work.")
    
    # Run the MCP server with appropriate transport
    mcp.run(transport=transport)