# Eval Module Tests

This directory contains comprehensive tests for the eval module's LLM wrapper functionality.

## Test Structure

### `test_llm_wrapper.py`
Tests for the LLM wrapper functionality:
- **ClaudeWrapper class**: API initialization, review extraction, response parsing
- **LLMResponse dataclass**: Response structure and error handling
- **Pydantic model validation**: Data validation for extracted review data
- **Error handling**: API failures, invalid responses, parsing errors
- **Real API integration**: Tests with actual Anthropic API calls

### `conftest.py`
Shared test fixtures and configuration:
- **Sample data**: Pre-configured review objects and extraction data
- **Environment setup**: Test environment configuration with .env loading
- **API key handling**: Environment variable management for real API tests

## Running Tests

### Run all tests:
```bash
pytest fetch_ai_restaurant_agent/src/eval/tests/
```

### Run specific test files:
```bash
# LLM wrapper tests
pytest fetch_ai_restaurant_agent/src/eval/tests/test_llm_wrapper.py
```

### Run with verbose output:
```bash
pytest -v fetch_ai_restaurant_agent/src/eval/tests/
```

### Run with coverage:
```bash
pytest --cov=fetch_ai_restaurant_agent.src.eval fetch_ai_restaurant_agent/src/eval/tests/
```

## Test Coverage

The tests cover:

### ✅ **LLM Wrapper**
- API initialization with environment variables
- Review extraction with success/failure scenarios
- Response parsing with Pydantic validation
- Error handling and retry logic
- Usage statistics calculation
- Real API integration with actual Anthropic calls

### ✅ **Pydantic Models**
- Data validation for all extraction schemas
- Field validation (ratings, sentiments, categories)
- Error handling for invalid data
- Model serialization/deserialization

## Mock Strategy

Tests use a combination of mocking and real API calls:

- **Real API calls**: For integration testing with actual Anthropic API
- **Environment variables**: Controlled test environment with .env loading
- **Error scenarios**: Mocked API failures for error handling tests

## Test Data

The tests use realistic sample data:

- **Sample reviews**: Google and Yelp reviews with various ratings
- **Extraction data**: Complete LLM extraction responses
- **Complex reviews**: Mixed sentiment reviews for comprehensive testing
- **Error scenarios**: API failures, invalid responses, parsing errors

## Dependencies

Test dependencies (in addition to main requirements):
- `pytest`: Testing framework
- `pytest-cov`: Coverage reporting
- `unittest.mock`: Mocking framework

## Environment Setup

Tests automatically configure:
- `ANTHROPIC_API_KEY`: Loaded from .env file for real API testing
- `LOG_LEVEL`: Set to DEBUG for detailed logging
- Environment variables: Automatically loaded from .env file

## Continuous Integration

These tests are designed to run in CI/CD pipelines:
- Real API calls for integration testing
- Deterministic results with controlled test data
- Fast execution with efficient test structure
- Comprehensive coverage of LLM wrapper functionality
