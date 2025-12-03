# Research: Tests & Evaluation Framework

**Feature**: 003-test-evaluation
**Date**: 2025-12-03

## Research Tasks Completed

### 1. Mocking LLM API Calls in ADK

**Decision**: Use `unittest.mock.patch` to mock Gemini model responses at the ADK level.

**Rationale**:
- ADK's `Gemini` class from `google.adk.models.google_llm` can be patched
- Mock the model's response method to return predefined responses
- This avoids actual API calls while testing agent behavior
- Deterministic responses ensure reproducible tests

**Alternatives considered**:
- VCR.py / responses library: Overkill for mocking LLM, better for HTTP APIs
- ADK's built-in test utilities: Not yet documented/stable
- Environment variable to disable API: Would require code changes

**Implementation pattern**:
```python
from unittest.mock import Mock, patch

@pytest.fixture
def mock_gemini():
    with patch('adk.agent.Gemini') as mock:
        mock_instance = Mock()
        mock_instance.generate.return_value = "Mocked response"
        mock.return_value = mock_instance
        yield mock_instance
```

### 2. Isolated SQLite Test Databases

**Decision**: Use pytest's `tmp_path` fixture to create ephemeral databases per test.

**Rationale**:
- `tmp_path` provides unique directories per test
- Databases are automatically cleaned up after tests
- No risk of test pollution between runs
- Matches production schema without modification

**Alternatives considered**:
- In-memory SQLite (`:memory:`): Doesn't test file I/O behavior
- Shared test database with cleanup: Risk of test pollution
- Docker containers: Overkill for SQLite

**Implementation pattern**:
```python
@pytest.fixture
def test_storage(tmp_path):
    db_path = tmp_path / "test_user.db"
    storage = StorageService("test_user", db_path=db_path)
    return storage
```

### 3. ADK Evaluation Patterns

**Decision**: Use JSON-based evalset files with custom evaluation runner.

**Rationale**:
- ADK evaluation support is evolving; JSON format is stable and portable
- Each scenario defines: input message, expected response patterns, pass criteria
- Evaluation runner loads scenarios, runs agent, compares outputs
- Supports regex patterns for flexible output matching

**Alternatives considered**:
- YAML evalsets: Less standard in Python ecosystem
- ADK native evalset (if available): API not stable yet
- Pytest parametrize: Less readable for non-developers

**Evaluation scenario schema**:
```json
{
  "scenario_id": "tutor_explain_concept",
  "description": "Tutor explains a concept from the PDF",
  "input": "Explain what an agent is in AI",
  "expected_patterns": [
    "agent",
    "(autonomous|independent|acts)"
  ],
  "required_tool_calls": ["fetch_info"],
  "max_response_time_ms": 5000,
  "pass_threshold": 0.8
}
```

### 4. pytest Best Practices for Agent Testing

**Decision**: Use pytest with async support, fixtures, and markers.

**Rationale**:
- `pytest-asyncio` for testing async agent flows
- Markers to separate unit, integration, evaluation tests
- Fixtures for shared setup (mock retriever, storage, agents)
- Coverage reporting with `pytest-cov`

**Implementation pattern**:
```python
# conftest.py
import pytest

pytest_plugins = ['pytest_asyncio']

@pytest.fixture
def mock_retriever():
    """Mock retriever that returns predefined chunks."""
    chunks = ["Chunk 1 about agents", "Chunk 2 about learning"]
    return SimpleRetriever(chunks)
```

### 5. GitHub Actions CI Configuration

**Decision**: Single workflow with matrix testing and coverage reporting.

**Rationale**:
- Matrix strategy for Python version compatibility
- Separate jobs for unit tests vs evaluations (evaluations may be slower/flaky)
- Coverage upload to GitHub PR comments
- Fail-fast disabled to see all failures

**Workflow structure**:
```yaml
name: Tests
on: [push, pull_request]
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r adk/requirements.txt
      - run: pip install pytest pytest-cov pytest-asyncio
      - run: pytest tests/unit --cov=adk --cov-report=xml
      - uses: codecov/codecov-action@v4

  evaluations:
    runs-on: ubuntu-latest
    needs: unit-tests
    # Only run on main branch to save API costs
    if: github.ref == 'refs/heads/main'
    steps:
      - run: python tests/evaluation/run_evaluation.py
```

### 6. Test Coverage Targets

**Decision**: Target 70% line coverage as minimum, with higher coverage for critical modules.

**Rationale**:
- 70% is achievable without testing every edge case
- storage.py should have 80%+ (critical for data integrity)
- tools.py and quiz_tools.py can be lower due to external dependencies
- Coverage check in CI ensures no regression

**Coverage thresholds**:
| Module | Target |
|--------|--------|
| adk/storage.py | 80% |
| adk/rag_setup.py | 75% |
| adk/tools.py | 65% |
| adk/quiz_tools.py | 70% |
| Overall | 70% |

## Dependencies to Add

```text
# Add to adk/requirements.txt or requirements-dev.txt
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-asyncio>=0.21.0
```

## Open Questions Resolved

1. **How to handle flaky LLM tests?** - Mock all LLM calls; evaluations run separately
2. **SQLite test isolation?** - Use tmp_path fixture for ephemeral databases
3. **Evaluation format?** - JSON files with pattern matching
4. **CI pipeline strategy?** - Unit tests on all PRs, evaluations on main only
