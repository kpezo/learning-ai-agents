# Quickstart: PDF Report Generator

**Feature**: 002-pdf-reports
**Date**: 2025-12-03

## Prerequisites

1. Existing learning data in SQLite storage (`data/{user_id}.db`)
2. At least one completed quiz session

## Installation

Add dependencies to `adk/requirements.txt`:

```text
reportlab>=4.0.0
svglib>=1.5.0
matplotlib>=3.7.0
```

Install:

```bash
pip install -r adk/requirements.txt
```

## Quick Usage

### CLI Usage

```bash
# Generate report for a user
python -m adk.reports.cli --user user123 --output report.pdf

# Generate with options
python -m adk.reports.cli \
  --user user123 \
  --output report.pdf \
  --days 30 \
  --format LETTER \
  --no-charts
```

### Python API Usage

```python
from adk.reports import generate_report, ReportConfig, DateRange
from datetime import datetime, timedelta

# Simple generation (last 30 days)
result = generate_report(user_id="user123")
if result.success:
    print(f"Report saved to: {result.file_path}")
else:
    print(f"Error: {result.error_message}")

# Custom configuration
config = ReportConfig(
    user_id="user123",
    date_range=DateRange(
        start=datetime.now() - timedelta(days=90),
        end=datetime.now()
    ),
    include_charts=True,
    include_recommendations=True,
    page_format="A4"
)
result = generate_report(config=config)
```

### ADK Agent Tool Usage

```python
from adk.reports.tools import generate_report_tool

# Add to agent tools
agent = Agent(
    name="ReportAgent",
    tools=[generate_report_tool],
    instruction="Help users generate and understand their progress reports."
)

# The agent can now respond to:
# "Generate a progress report for me"
# "Show me my learning summary"
# "Create a PDF of my quiz results"
```

## Report Sections

The generated PDF includes:

1. **Executive Summary** (FR-002)
   - Overall mastery percentage
   - Total quizzes completed
   - Time spent learning
   - Concepts covered

2. **Concept Mastery Breakdown** (FR-003, FR-004)
   - Table grouped by tier (Mastered, In Progress, Needs Practice)
   - Mastery percentage per concept
   - Practice count and trend indicators

3. **Learning Analytics** (FR-005, FR-006, FR-007)
   - Score progression chart
   - Time distribution by topic
   - Activity heatmap (optional)

4. **Recommendations** (FR-008)
   - Prioritized list of suggested actions
   - Focus areas for improvement
   - Next steps for advancement

## Example Output

```
┌─────────────────────────────────────────┐
│       Learning Progress Report          │
│       user123 | 2025-12-03              │
├─────────────────────────────────────────┤
│                                         │
│  Executive Summary                      │
│  ─────────────────                      │
│  Overall Mastery: 72%                   │
│  Quizzes Completed: 15                  │
│  Time Spent: 4h 32m                     │
│  Concepts Covered: 23                   │
│                                         │
│  Mastery Breakdown:                     │
│    ✓ Mastered (8)                       │
│    ◐ In Progress (10)                   │
│    ○ Needs Practice (5)                 │
│                                         │
├─────────────────────────────────────────┤
│  [Score Progression Chart]              │
│  [Time Distribution Chart]              │
├─────────────────────────────────────────┤
│  Recommendations                        │
│  1. Review: Variables - declining trend │
│  2. Practice: Loops - 45% mastery       │
│  3. Advance: Functions - ready for next │
└─────────────────────────────────────────┘
```

## Error Handling

| Scenario | Behavior |
|----------|----------|
| No quiz data | Returns error, suggests completing a quiz first |
| Missing user | Returns error with user not found message |
| Partial data | Generates report with available sections, notes gaps |
| Chart failure | Falls back to text-only report |

## File Storage

Reports are saved to:
- Default: `data/reports/{user_id}_{timestamp}.pdf`
- Custom: Specify via `--output` flag or `output_path` parameter

## Performance Notes

- Generation time: 2-5 seconds for typical data (50 quizzes)
- Memory usage: ~30-50 MB during generation
- File size: 800KB-1.5MB with charts

## Next Steps

1. Run `/speckit.tasks` to generate implementation tasks
2. Implement `adk/reports/` module structure
3. Add tests in `tests/unit/test_reports/`
4. Integrate with existing agent tools
