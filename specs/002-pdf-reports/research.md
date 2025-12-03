# Research: PDF Report Generator

**Feature**: 002-pdf-reports
**Date**: 2025-12-03

## PDF Generation Library

### Decision: ReportLab

**Version**: 4.4.5
**License**: BSD-2-Clause (OSS-friendly)
**Installation**: `pip install reportlab`

### Rationale

1. **Best fit for programmatic report generation**: ReportLab's canvas model provides precise layout control for complex multi-section reports with charts
2. **Native graphics support**: Built-in `reportlab.graphics` for vector charts that render sharp at any zoom
3. **Industry standard**: 4.7M monthly downloads, proven for financial/data-heavy reports
4. **Fast performance**: C-backed implementation, fastest among Python PDF libraries
5. **Print-friendly**: Automatic page breaking, header/footer callbacks, font embedding

### Alternatives Considered

| Library | Pros | Cons | Verdict |
|---------|------|------|---------|
| **fpdf2** | Simple API, fast for text | LGPL license, limited layout control, no native vector graphics | Better for invoices, not analytics reports |
| **WeasyPrint** | HTML/CSS syntax, modern styling | Requires HTML templates, system deps (Cairo), slower | Overkill for programmatic generation |

## Chart Embedding Strategy

### Decision: SVG via svglib

```python
from io import BytesIO
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF

# Save matplotlib as SVG
svg_buffer = BytesIO()
fig.savefig(svg_buffer, format='svg', bbox_inches='tight')
svg_buffer.seek(0)

# Convert and embed
drawing = svg2rlg(svg_buffer)
renderPDF.draw(drawing, canvas, x, y)
```

### Rationale

- **Vector graphics**: Charts remain sharp at any zoom level
- **Small file size**: 80% smaller than high-res PNG
- **Print quality**: Perfect for A4/Letter printing
- **Memory efficient**: No need for high-DPI raster images

### Alternative: PNG embedding

```python
from io import BytesIO
from reportlab.lib.utils import ImageReader

img_buffer = BytesIO()
plt.savefig(img_buffer, format='png', dpi=200)
canvas.drawImage(ImageReader(img_buffer), x, y, width=w, height=h)
```

Use only if SVG conversion fails for complex charts.

## Grayscale Printing Compatibility

### Decision: Matplotlib grayscale style + pattern fills

```python
import matplotlib.pyplot as plt

plt.style.use('grayscale')

# Use line styles for differentiation
line_styles = ['-', '--', '-.', ':']
markers = ['o', 's', '^', 'D']

for i, (label, values) in enumerate(data.items()):
    ax.plot(values,
            linestyle=line_styles[i % 4],
            marker=markers[i % 4],
            color='black')
```

### Rationale

- Line styles and markers distinguish series without color
- Native grayscale rendering (no post-processing needed)
- Consistent across print/digital viewing

## Performance Characteristics

| Metric | Expected Value | Meets SC-001? |
|--------|---------------|---------------|
| Generation time (50 quizzes) | 3-5 seconds | ✅ (<10s) |
| Memory peak | 30-50 MB | ✅ Acceptable |
| File size | 800KB-1.5MB | ✅ Shareable |

### Optimization Strategies

1. Use vector graphics (SVG) instead of high-res PNG
2. Disable shape checking in production: `reportlab.rl_config.shapeChecking = 0`
3. Generate charts at 150 DPI (not 300+)
4. Use in-memory buffers instead of temp files
5. Lazy load historical data (last 30 days default)

## Dependencies to Add

```text
# adk/requirements.txt additions
reportlab>=4.0.0       # PDF generation
svglib>=1.5.0          # Vector chart embedding
matplotlib>=3.7.0      # Chart generation
```

Note: `pillow` is likely already installed as a transitive dependency.

## Key Implementation Patterns

### 1. Document Template with Header/Footer

```python
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch

def add_header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica-Bold', 10)
    canvas.drawString(0.75*inch, 10.5*inch, "Learning Progress Report")
    canvas.setFont('Helvetica', 9)
    canvas.drawRightString(8*inch, 0.5*inch, f"Page {doc.page}")
    canvas.restoreState()

doc = SimpleDocTemplate("report.pdf", pagesize=LETTER,
    topMargin=0.75*inch, bottomMargin=0.75*inch)
doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
```

### 2. Section Grouping (No Mid-Section Breaks)

```python
from reportlab.platypus import KeepTogether, PageBreak

story.append(KeepTogether([
    Paragraph("Executive Summary", heading_style),
    create_summary_table(data)
]))
story.append(PageBreak())
```

### 3. Mastery Table with Visual Progress Bars

```python
def create_mastery_table(concepts):
    data = [['Concept', 'Mastery', 'Progress', 'Practices', 'Trend']]
    for c in concepts:
        filled = int(c.mastery_level * 10)
        bar = '█' * filled + '░' * (10 - filled)
        trend = '↑' if improving(c) else ('↓' if declining(c) else '→')
        data.append([c.concept_name, f"{c.mastery_level*100:.0f}%", bar, str(c.times_seen), trend])
    return Table(data)
```

### 4. Integration with Storage Layer

```python
from adk.storage import get_storage

def collect_report_data(user_id: str):
    storage = get_storage(user_id)
    return {
        'stats': storage.get_user_stats(),
        'concepts': storage.get_all_mastery(),
        'weak_concepts': storage.get_weak_concepts(threshold=0.5),
        'quiz_history': storage.get_quiz_history(limit=50),
    }
```

## Accessibility Notes

For basic accessibility (without full PDF/UA compliance):

- Use heading hierarchy (Heading1, Heading2)
- Include chart titles as text before each visualization
- Use minimum 10pt fonts
- Maintain high contrast (>4.5:1 ratio)
- Use Platypus flowables for logical reading order

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Large historical datasets cause memory issues | Paginate to last 30 days by default |
| Complex charts slow generation | Use vector graphics, cache common visualizations |
| PDF rendering differs across viewers | Use standard fonts, test on Adobe/Preview/Chrome |
| Print quality issues | Use vector graphics, validate on grayscale printer early |
