# Quickstart: Tests & Evaluation Framework

**Feature**: 003-test-evaluation

## Prerequisites

- Python 3.11+
- Project dependencies installed: `pip install -r adk/requirements.txt`
- Test dependencies: `pip install pytest pytest-cov pytest-asyncio`

## Running Tests

### Run All Unit Tests

```bash
# From repository root
pytest tests/unit -v
```

### Run Tests with Coverage

```bash
pytest tests/unit --cov=adk --cov-report=term-missing --cov-report=html
# Open htmlcov/index.html for detailed report
```

### Run Specific Test File

```bash
pytest tests/unit/test_storage.py -v
```

### Run Specific Test

```bash
pytest tests/unit/test_storage.py::test_quiz_lifecycle -v
```

### Run Tests by Marker

```bash
# Run only fast unit tests
pytest tests/unit -m "not slow"

# Run integration tests
pytest tests/integration -v
```

## Running Evaluations

### Run All Evaluation Scenarios

```bash
python tests/evaluation/run_evaluation.py
```

### Run Evaluations for Specific Agent

```bash
python tests/evaluation/run_evaluation.py --agent tutor
```

### Run with Verbose Output

```bash
python tests/evaluation/run_evaluation.py --verbose
```

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── unit/
│   ├── test_tools.py        # RAG tool tests
│   ├── test_quiz_tools.py   # Quiz flow tests
│   ├── test_storage.py      # Database tests
│   └── test_rag_setup.py    # Retriever tests
├── integration/
│   └── test_agent_flow.py   # Multi-agent tests
└── evaluation/
    ├── evalsets/            # Scenario JSON files
    └── run_evaluation.py    # Evaluation runner
```

## Writing New Tests

### Unit Test Template

```python
# tests/unit/test_example.py
import pytest
from adk.storage import StorageService

@pytest.fixture
def storage(tmp_path):
    """Create isolated test database."""
    db_path = tmp_path / "test.db"
    return StorageService("test_user", db_path=db_path)

def test_example(storage):
    """Test description."""
    # Arrange
    expected = "value"

    # Act
    result = storage.some_method()

    # Assert
    assert result == expected
```

### Adding Evaluation Scenarios

1. Edit or create evalset file in `tests/evaluation/evalsets/`
2. Follow schema from `specs/003-test-evaluation/contracts/evalset-schema.json`
3. Run evaluation to verify

```json
{
  "scenario_id": "new_scenario",
  "description": "Test new agent behavior",
  "input": "User message here",
  "expected_patterns": ["pattern1", "pattern2"],
  "required_tool_calls": ["fetch_info"]
}
```

## CI/CD Integration

Tests run automatically on:
- Every push to any branch (unit tests only)
- Pull requests to main (unit tests + coverage check)
- Merges to main (full evaluation suite)

Check `.github/workflows/test.yml` for configuration.

## Common Issues

### Tests Fail with "Retriever not initialized"

Ensure mock fixtures are used. Real retriever requires PDF file:
```python
@pytest.fixture
def mock_retriever(monkeypatch):
    # See conftest.py for full implementation
```

### Database Lock Errors

Use `tmp_path` fixture for isolated databases:
```python
def test_something(tmp_path):
    db_path = tmp_path / "test.db"
    storage = StorageService("user", db_path=db_path)
```

### Async Test Issues

Mark async tests and use proper runner:
```python
import pytest

@pytest.mark.asyncio
async def test_async_operation():
    result = await some_async_function()
    assert result is not None
```
