# Quickstart: Advanced Pedagogical Metrics

**Feature**: 008-pedagogical-metrics

This guide covers integration of the pedagogical metrics system with the existing ADK educational agent.

---

## Prerequisites

- Python 3.11+
- Existing `adk/` module installed
- NumPy (for calculations)

```bash
pip install numpy
```

---

## Basic Usage

### 1. BKT Mastery Calculation

```python
from adk.metrics.bkt import BKTCalculator

# Initialize calculator with default parameters
bkt = BKTCalculator(p_l0=0.1, p_t=0.3, p_g=0.2, p_s=0.1)

# Simulate a sequence of answers
answers = [True, True, False, True, True, True]

for correct in answers:
    result = bkt.update(correct)
    print(f"Correct: {correct}, Mastery: {result.mastery_probability:.2%}")

# Check if mastered
if bkt.is_mastered():
    print("Concept mastered!")
```

**Expected output:**
```
Correct: True, Mastery: 35.29%
Correct: True, Mastery: 58.03%
Correct: False, Mastery: 46.84%
Correct: True, Mastery: 68.20%
Correct: True, Mastery: 82.91%
Correct: True, Mastery: 92.04%
```

### 2. IRT Probability Calculation

```python
from adk.metrics.irt import IRTCalculator

irt = IRTCalculator()

# Calculate probability for a learner (theta=1.0) on a medium question
prob = irt.probability(
    theta=1.0,      # Above-average ability
    a=1.0,          # Average discrimination
    b=0.5,          # Slightly hard
    c=0.25          # 4-option MC
)
print(f"P(correct) = {prob:.2%}")  # ~66%

# Estimate ability from response pattern
responses = [True, True, False, True, False, True]
difficulties = [-1.0, 0.0, 0.5, 0.0, 1.0, -0.5]

ability = irt.estimate_theta(responses, difficulties)
print(f"Estimated ability: {ability.theta:.2f} (SE: {ability.standard_error:.2f})")
```

### 3. ZPD Evaluation

```python
from adk.metrics.zpd import ZPDEvaluator

zpd = ZPDEvaluator()

# Check ZPD status based on recent performance
recent_results = [True, True, False, True, True]  # 4/5 = 80%
status = zpd.evaluate(recent_results)

print(f"Zone: {status.zone.value}")
print(f"Success rate: {status.success_rate:.0%}")
print(f"Recommended difficulty: {status.recommended_difficulty}")
```

### 4. Behavioral Detection

```python
from adk.metrics.behavioral import BehavioralAnalyzer

analyzer = BehavioralAnalyzer()

# Analyze a potentially frustrated learner
result = analyzer.analyze(
    response_time_ms=15000,    # Took 15 seconds
    expected_time_ms=5000,     # Expected 5 seconds
    hints_used=3,              # Used 3 hints
    consecutive_incorrect=2    # 2 wrong in a row
)

print(f"Indicator: {result.indicator.value}")
print(f"Confidence: {result.confidence:.0%}")
```

---

## Integration with Quiz Tools

### Update `advance_quiz()` to Use BKT

```python
from adk.metrics.bkt import BKTCalculator
from adk.storage import get_storage

def advance_quiz_with_bkt(
    correct: bool,
    concept_name: str,
    response_time_ms: int = None,
    tool_context = None
):
    """Enhanced quiz advancement with BKT mastery tracking."""

    user_id = _get_user_id(tool_context)
    storage = get_storage(user_id)

    # Get or create BKT calculator for this concept
    bkt = storage.get_bkt_model(concept_name)
    if not bkt:
        bkt = BKTCalculator()
        storage.create_bkt_model(user_id, concept_name, bkt)

    # Update mastery
    result = bkt.update(correct)

    # Persist to storage
    storage.save_bkt_state(user_id, concept_name, bkt)

    return {
        "status": "success",
        "mastery_probability": result.mastery_probability,
        "is_mastered": result.is_mastered,
        "confidence_interval": (result.confidence_lower, result.confidence_upper)
    }
```

### Add ZPD-Based Question Selection

```python
from adk.metrics.zpd import ZPDEvaluator
from adk.metrics.irt import IRTCalculator

def select_next_question(user_id: str, concept_name: str, question_pool: list):
    """Select optimal question based on ZPD and ability."""

    storage = get_storage(user_id)

    # Get current ability estimate
    ability = storage.get_learner_ability(user_id)
    theta = ability.theta if ability else 0.0

    # Get ZPD status
    recent = storage.get_recent_results(user_id, concept_name, limit=5)
    zpd = ZPDEvaluator()
    zpd_status = zpd.evaluate(recent)

    # Select question at appropriate difficulty
    irt = IRTCalculator()
    target_difficulty = zpd_status.recommended_difficulty

    # Filter to appropriate difficulty range
    candidates = [q for q in question_pool
                  if abs(q['difficulty_b'] - target_difficulty) < 0.5]

    # Select highest information question
    best = irt.select_optimal_question(theta, candidates)
    return best
```

---

## Storage Integration

### Initialize New Tables

```python
from adk.storage import StorageService

class MetricsStorageService(StorageService):
    """Extended storage service with pedagogical metrics tables."""

    def _init_db(self):
        super()._init_db()

        # Load and execute metrics schema
        with open('specs/008-pedagogical-metrics/contracts/storage_schema.sql') as f:
            schema = f.read()

        with self._get_conn() as conn:
            conn.executescript(schema)
```

### BKT CRUD Operations

```python
def save_bkt_state(self, user_id: str, concept_name: str, bkt: BKTCalculator):
    """Save BKT state to database."""
    with self._get_conn() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO bkt_parameters
            (user_id, concept_name, p_l0, p_t, p_g, p_s,
             p_l_current, confidence_lower, confidence_upper,
             observations, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, concept_name,
            bkt.p_l0, bkt.p_t, bkt.p_g, bkt.p_s,
            bkt.p_l, bkt.confidence_lower, bkt.confidence_upper,
            bkt.observations, datetime.utcnow().isoformat()
        ))

def get_bkt_model(self, user_id: str, concept_name: str) -> Optional[BKTCalculator]:
    """Load BKT model from database."""
    with self._get_conn() as conn:
        row = conn.execute("""
            SELECT * FROM bkt_parameters
            WHERE user_id = ? AND concept_name = ?
        """, (user_id, concept_name)).fetchone()

    if not row:
        return None

    return BKTCalculator(
        p_l0=row['p_l0'],
        p_t=row['p_t'],
        p_g=row['p_g'],
        p_s=row['p_s'],
        p_l_current=row['p_l_current']
    )
```

---

## ADK Tool Wrappers

### Create Metrics Tools

```python
from google.adk.tools import FunctionTool

def _get_mastery_bkt(concept_name: str, tool_context=None) -> dict:
    """Get BKT-based mastery for a concept."""
    user_id = _get_user_id(tool_context)
    storage = get_storage(user_id)

    bkt = storage.get_bkt_model(user_id, concept_name)
    if not bkt:
        return {"status": "no_data", "concept": concept_name}

    return {
        "status": "success",
        "concept": concept_name,
        "mastery_probability": bkt.p_l,
        "is_mastered": bkt.p_l >= 0.95,
        "observations": bkt.observations
    }

get_mastery_bkt_tool = FunctionTool(func=_get_mastery_bkt)
```

---

## Testing

### Unit Test Example

```python
import pytest
from adk.metrics.bkt import BKTCalculator

def test_bkt_mastery_increases_on_correct():
    bkt = BKTCalculator(p_l0=0.5)
    initial = bkt.p_l

    bkt.update(correct=True)

    assert bkt.p_l > initial

def test_bkt_mastery_decreases_on_incorrect():
    bkt = BKTCalculator(p_l0=0.5)
    initial = bkt.p_l

    bkt.update(correct=False)

    assert bkt.p_l < initial

def test_bkt_reaches_mastery():
    bkt = BKTCalculator(p_l0=0.1)

    # Simulate 10 correct answers
    for _ in range(10):
        bkt.update(correct=True)

    assert bkt.is_mastered()
    assert bkt.p_l >= 0.95
```

### Integration Test Example

```python
import pytest
from adk.storage import get_storage
from adk.metrics.bkt import BKTCalculator

@pytest.fixture
def test_storage(tmp_path):
    """Create test storage with metrics tables."""
    storage = MetricsStorageService("test_user", tmp_path / "test.db")
    return storage

def test_bkt_persistence(test_storage):
    # Create and save BKT model
    bkt = BKTCalculator()
    bkt.update(True)
    bkt.update(True)

    test_storage.save_bkt_state("test_user", "algebra", bkt)

    # Load and verify
    loaded = test_storage.get_bkt_model("test_user", "algebra")

    assert loaded is not None
    assert loaded.p_l == pytest.approx(bkt.p_l, abs=0.001)
    assert loaded.observations == 2
```

---

## Migration from Simple Mastery

To migrate existing users from simple ratio mastery to BKT:

```python
def migrate_to_bkt(user_id: str):
    """Migrate user from simple mastery to BKT."""
    storage = get_storage(user_id)

    # Get all existing mastery records
    existing = storage.get_all_mastery()

    for record in existing:
        # Create BKT model with prior based on existing mastery
        bkt = BKTCalculator(
            p_l0=record.mastery_level,  # Start from existing level
            p_t=0.3,
            p_g=0.2,
            p_s=0.1
        )

        # Set observations from history
        bkt.observations = record.times_seen
        bkt.p_l = record.mastery_level

        # Save BKT model
        storage.save_bkt_state(user_id, record.concept_name, bkt)
```
