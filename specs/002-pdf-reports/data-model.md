# Data Model: PDF Report Generator

**Feature**: 002-pdf-reports
**Date**: 2025-12-03

## Entity Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            Report Generation                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐      ┌─────────────────┐      ┌─────────────────┐    │
│  │ ReportConfig │──────│ ProgressReport  │──────│ GeneratedReport │    │
│  │  (input)     │      │  (processing)   │      │   (output)      │    │
│  └──────────────┘      └─────────────────┘      └─────────────────┘    │
│         │                      │                         │              │
│         │                      │                         │              │
│         ▼                      ▼                         ▼              │
│  ┌──────────────┐      ┌─────────────────┐      ┌─────────────────┐    │
│  │ DateRange    │      │ MasterySummary  │      │  ReportMetadata │    │
│  └──────────────┘      │ ConceptBreakdown│      │  (stored)       │    │
│                        │ LearningAnalytics│     └─────────────────┘    │
│                        │ Recommendation  │                             │
│                        └─────────────────┘                             │
└─────────────────────────────────────────────────────────────────────────┘
```

## Entities

### ReportConfig (Input)

Configuration for report generation request.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| user_id | str | ✅ | - | User identifier from storage |
| date_range | DateRange | ❌ | Last 30 days | Period to include in report |
| include_charts | bool | ❌ | True | Whether to generate visualizations |
| include_recommendations | bool | ❌ | True | Whether to generate recommendations |
| format | str | ❌ | "A4" | Page size: "A4" or "LETTER" |

```python
@dataclass
class ReportConfig:
    user_id: str
    date_range: Optional[DateRange] = None  # None = last 30 days
    include_charts: bool = True
    include_recommendations: bool = True
    format: str = "A4"  # or "LETTER"
```

### DateRange

Time period for report data.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| start | datetime | ✅ | Start of period (inclusive) |
| end | datetime | ✅ | End of period (inclusive) |

```python
@dataclass
class DateRange:
    start: datetime
    end: datetime

    @classmethod
    def last_n_days(cls, n: int) -> "DateRange":
        end = datetime.utcnow()
        start = end - timedelta(days=n)
        return cls(start=start, end=end)
```

### ProgressReport (Processing)

Aggregated data structure for report generation. Not persisted.

| Field | Type | Description |
|-------|------|-------------|
| user_id | str | User identifier |
| generated_at | datetime | Report generation timestamp |
| summary | MasterySummary | Executive summary data |
| concepts | List[ConceptBreakdown] | Per-concept mastery details |
| analytics | LearningAnalytics | Time-series data for charts |
| recommendations | List[Recommendation] | Generated suggestions |

```python
@dataclass
class ProgressReport:
    user_id: str
    generated_at: datetime
    summary: MasterySummary
    concepts: List[ConceptBreakdown]
    analytics: LearningAnalytics
    recommendations: List[Recommendation]
```

### MasterySummary (FR-002)

Executive summary statistics.

| Field | Type | Description |
|-------|------|-------------|
| overall_mastery_pct | float | Average mastery across all concepts (0.0-100.0) |
| total_quizzes | int | Number of completed quizzes |
| total_time_minutes | int | Total time spent (from session logs) |
| concepts_covered | int | Number of unique concepts seen |
| mastered_count | int | Concepts with mastery >= 85% |
| in_progress_count | int | Concepts with mastery 50-85% |
| needs_practice_count | int | Concepts with mastery < 50% |
| date_range | DateRange | Period covered by report |

```python
@dataclass
class MasterySummary:
    overall_mastery_pct: float  # 0.0 - 100.0
    total_quizzes: int
    total_time_minutes: int
    concepts_covered: int
    mastered_count: int        # >= 85%
    in_progress_count: int     # 50% - 84%
    needs_practice_count: int  # < 50%
    date_range: DateRange
```

### ConceptBreakdown (FR-003, FR-004)

Individual concept mastery details for the report.

| Field | Type | Description |
|-------|------|-------------|
| concept_name | str | Name of the concept |
| mastery_level | float | Current mastery (0.0-1.0) |
| mastery_tier | MasteryTier | Categorization: MASTERED, IN_PROGRESS, NEEDS_PRACTICE |
| times_practiced | int | Total practice count |
| times_correct | int | Correct answer count |
| trend | TrendDirection | Performance trend: IMPROVING, STABLE, DECLINING |
| last_practiced | datetime | Most recent practice timestamp |
| knowledge_type | str | declarative/procedural/conditional |

```python
class MasteryTier(str, Enum):
    MASTERED = "mastered"           # >= 85%
    IN_PROGRESS = "in_progress"     # 50% - 84%
    NEEDS_PRACTICE = "needs_practice"  # < 50%

class TrendDirection(str, Enum):
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"

@dataclass
class ConceptBreakdown:
    concept_name: str
    mastery_level: float          # 0.0 - 1.0
    mastery_tier: MasteryTier
    times_practiced: int
    times_correct: int
    trend: TrendDirection
    last_practiced: datetime
    knowledge_type: str           # declarative/procedural/conditional

    @classmethod
    def from_mastery(cls, m: ConceptMastery, trend: TrendDirection) -> "ConceptBreakdown":
        if m.mastery_level >= 0.85:
            tier = MasteryTier.MASTERED
        elif m.mastery_level >= 0.50:
            tier = MasteryTier.IN_PROGRESS
        else:
            tier = MasteryTier.NEEDS_PRACTICE

        return cls(
            concept_name=m.concept_name,
            mastery_level=m.mastery_level,
            mastery_tier=tier,
            times_practiced=m.times_seen,
            times_correct=m.times_correct,
            trend=trend,
            last_practiced=datetime.fromisoformat(m.last_seen),
            knowledge_type=m.knowledge_type
        )
```

### LearningAnalytics (FR-005, FR-006, FR-007)

Time-series data for visualizations.

| Field | Type | Description |
|-------|------|-------------|
| score_progression | List[ScorePoint] | Quiz scores over time |
| difficulty_changes | List[DifficultyPoint] | Difficulty level changes |
| time_per_topic | Dict[str, int] | Minutes spent per topic |
| session_dates | List[date] | Dates with activity (for heatmap) |

```python
@dataclass
class ScorePoint:
    date: date
    score: float         # 0.0 - 1.0
    topic: str
    quiz_id: int

@dataclass
class DifficultyPoint:
    date: date
    level: int           # 1-6
    topic: str

@dataclass
class LearningAnalytics:
    score_progression: List[ScorePoint]
    difficulty_changes: List[DifficultyPoint]
    time_per_topic: Dict[str, int]  # topic -> minutes
    session_dates: List[date]       # for activity heatmap
```

### Recommendation (FR-008)

Personalized learning suggestion.

| Field | Type | Description |
|-------|------|-------------|
| type | RecommendationType | REVIEW, PRACTICE, ADVANCE |
| priority | int | 1 (highest) to 3 (lowest) |
| target | str | Concept or topic name |
| reasoning | str | Why this recommendation |
| action | str | Suggested action for learner |

```python
class RecommendationType(str, Enum):
    REVIEW = "review"       # Review weak concept
    PRACTICE = "practice"   # More practice needed
    ADVANCE = "advance"     # Ready for harder content

@dataclass
class Recommendation:
    type: RecommendationType
    priority: int           # 1-3, lower is more important
    target: str             # concept or topic name
    reasoning: str          # why this recommendation
    action: str             # what the learner should do
```

### GeneratedReport (Output, FR-015)

Stored metadata for generated reports (optional persistence).

| Field | Type | Description |
|-------|------|-------------|
| id | int | Auto-increment ID |
| user_id | str | User identifier |
| generated_at | datetime | When report was created |
| file_path | str | Path to stored PDF file |
| date_range_start | datetime | Report period start |
| date_range_end | datetime | Report period end |
| summary_json | str | Cached summary data as JSON |

```python
@dataclass
class GeneratedReport:
    id: Optional[int] = None
    user_id: str = ""
    generated_at: str = ""
    file_path: str = ""
    date_range_start: str = ""
    date_range_end: str = ""
    summary_json: str = ""  # Cached MasterySummary as JSON
```

## Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Data Collection                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  StorageService                      DataCollector                       │
│  ┌─────────────────┐                ┌─────────────────┐                 │
│  │ quiz_results    │────────────────│ collect_data()  │                 │
│  │ concept_mastery │────────────────│                 │                 │
│  │ session_logs    │────────────────│     Returns:    │                 │
│  │ knowledge_gaps  │────────────────│ ProgressReport  │                 │
│  └─────────────────┘                └─────────────────┘                 │
│                                              │                           │
│                                              ▼                           │
│                                     ┌─────────────────┐                 │
│                                     │ ReportGenerator │                 │
│                                     │                 │                 │
│                                     │  render_pdf()   │                 │
│                                     └─────────────────┘                 │
│                                              │                           │
│                                              ▼                           │
│                                     ┌─────────────────┐                 │
│                                     │  PDF Document   │                 │
│                                     │  (.pdf file)    │                 │
│                                     └─────────────────┘                 │
└─────────────────────────────────────────────────────────────────────────┘
```

## Validation Rules

### ReportConfig
- `user_id` must exist in storage
- `date_range.start` must be before `date_range.end`
- If no quiz data exists for user, return error (FR-009)

### MasterySummary
- `overall_mastery_pct` must be 0.0-100.0
- `mastered_count + in_progress_count + needs_practice_count == concepts_covered`

### ConceptBreakdown
- `mastery_level` must be 0.0-1.0
- `times_correct <= times_practiced`
- `mastery_tier` must match `mastery_level` thresholds

### Recommendation
- At least 1 recommendation if `needs_practice_count > 0`
- `priority` must be 1-3
- `target` must reference a valid concept or topic

## State Transitions

### Trend Calculation

```
If mastery improved by > 10% in last 7 days:
    trend = IMPROVING
Else if mastery declined by > 10% in last 7 days:
    trend = DECLINING
Else:
    trend = STABLE
```

### Mastery Tier Assignment

```
If mastery_level >= 0.85:
    tier = MASTERED
Else if mastery_level >= 0.50:
    tier = IN_PROGRESS
Else:
    tier = NEEDS_PRACTICE
```

## Integration with Existing Schema

The report generator reads from existing tables in `adk/storage.py`:

| Report Entity | Source Table(s) | Query Pattern |
|---------------|-----------------|---------------|
| MasterySummary | quiz_results, concept_mastery | Aggregate stats |
| ConceptBreakdown | concept_mastery | All rows for user |
| ScoreProgression | quiz_results | Time-ordered history |
| TimePerTopic | session_logs | Group by topic, sum duration |

No new database tables required for core functionality. Optional `generated_reports` table for persistence (FR-015).
