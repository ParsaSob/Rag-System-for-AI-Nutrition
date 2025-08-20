import os
import pytest
from unittest.mock import patch

# Mock environment variables before importing the module
os.environ["OPENAI_API_KEY"] = "test-api-key"

from src.document_processor import DocumentProcessor

def test_document_processor_initialization():
    """Test that DocumentProcessor initializes correctly."""
    processor = DocumentProcessor()
    assert processor is not None
    assert processor.chunks == []
    assert processor.chunk_embeddings == []

def test_count_tokens():
    """Test token counting functionality."""
    from src.utils import count_tokens
    
    text = "Hello, world!"
    tokens = count_tokens(text)
    assert tokens > 0
    assert isinstance(tokens, int)

def test_estimate_cost():
    """Test cost estimation functionality."""
    from src.utils import estimate_cost
    
    input_tokens = 1000
    output_tokens = 500
    costs = estimate_cost(input_tokens, output_tokens)
    
    assert isinstance(costs, dict)
    assert "input_cost" in costs
    assert "output_cost" in costs
    assert "total_cost" in costs
    assert all(isinstance(cost, float) for cost in costs.values()) 