import tiktoken
import logging
from typing import Dict, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenAI pricing (as of March 2024)
# GPT-4 Turbo (128K context)
OPENAI_PRICING = {
    "input": 0.01,    # $0.01 per 1K tokens
    "output": 0.03    # $0.03 per 1K tokens
}

def count_tokens(text: str) -> int:
    """
    Count the number of tokens in a text string using tiktoken.
    
    Args:
        text (str): The text to count tokens for
        
    Returns:
        int: Number of tokens in the text
    """
    try:
        # Using GPT-4 Turbo encoding
        encoding = tiktoken.encoding_for_model("gpt-4-turbo-preview")
        return len(encoding.encode(text))
    except Exception as e:
        logger.error(f"Error counting tokens: {str(e)}")
        return 0

def estimate_cost(input_tokens: int, output_tokens: int) -> dict:
    """
    Estimate the cost of an API call based on token usage.
    
    Args:
        input_tokens (int): Number of input tokens
        output_tokens (int): Number of output tokens
        
    Returns:
        dict: Dictionary containing input cost, output cost, and total cost
    """
    try:
        # Convert tokens to thousands for pricing calculation
        input_cost = (input_tokens / 1000) * OPENAI_PRICING["input"]
        output_cost = (output_tokens / 1000) * OPENAI_PRICING["output"]
        total_cost = input_cost + output_cost
        
        return {
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost
        }
    except Exception as e:
        logger.error(f"Error estimating cost: {str(e)}")
        return {
            "input_cost": 0,
            "output_cost": 0,
            "total_cost": 0
        }

def format_token_info(input_tokens: int, output_tokens: int, costs: dict) -> str:
    """
    Format token usage and cost information for display.
    
    Args:
        input_tokens (int): Number of input tokens
        output_tokens (int): Number of output tokens
        costs (dict): Dictionary containing cost information
        
    Returns:
        str: Formatted string with token and cost information
    """
    try:
        return f"""
**Model Information:**
- Model: GPT-4 Turbo (128K context)
- Pricing: ${OPENAI_PRICING['input']:.3f}/1K input tokens, ${OPENAI_PRICING['output']:.3f}/1K output tokens

**Token Usage:**
- Input Tokens: {input_tokens:,}
- Output Tokens: {output_tokens:,}
- Total Tokens: {input_tokens + output_tokens:,}

**Cost Estimation:**
- Input Cost: ${costs['input_cost']:.4f}
- Output Cost: ${costs['output_cost']:.4f}
- Total Cost: ${costs['total_cost']:.4f}
"""
    except Exception as e:
        logger.error(f"Error formatting token info: {str(e)}")
        return "Error calculating token usage and costs." 