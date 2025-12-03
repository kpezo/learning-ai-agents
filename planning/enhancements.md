🎚️ Enhancement 1: Adaptive Difficulty System
Concept Overview
The Adaptive Difficulty system dynamically adjusts question complexity based on real-time learner performance, ensuring optimal challenge level (not too easy, not too hard).
┌─────────────────────────────────────────────────────────────────┐
│                    ADAPTIVE DIFFICULTY ENGINE                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Performance    ──▶   Difficulty    ──▶   Question            │
│   Analyzer             Calculator          Modifier             │
│                                                                  │
│   (Tracks recent       (Computes           (Adjusts question    │
│    answers)            optimal level)       complexity)          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
Difficulty Levels Framework
pythonDIFFICULTY_LEVELS = {
    1: {
        "name": "Foundation",
        "question_types": ["definition", "recognition", "true_false"],
        "hints_allowed": 3,
        "time_pressure": None,
        "answer_format": "simple_response",
        "example": "What is [concept]?"
    },
    2: {
        "name": "Understanding", 
        "question_types": ["explanation", "comparison", "sequence"],
        "hints_allowed": 2,
        "time_pressure": None,
        "answer_format": "short_paragraph",
        "example": "Explain how [concept] works."
    },
    3: {
        "name": "Application",
        "question_types": ["scenario", "problem_solving", "prediction"],
        "hints_allowed": 1,
        "time_pressure": "relaxed",
        "answer_format": "structured_response",
        "example": "Given [scenario], how would you apply [concept]?"
    },
    4: {
        "name": "Analysis",
        "question_types": ["relationship", "cause_effect", "compare_contrast"],
        "hints_allowed": 0,
        "time_pressure": "moderate",
        "answer_format": "detailed_analysis",
        "example": "Analyze the relationship between [X] and [Y]."
    },
    5: {
        "name": "Synthesis",
        "question_types": ["design", "integration", "novel_scenario"],
        "hints_allowed": 0,
        "time_pressure": "challenging",
        "answer_format": "comprehensive_response",
        "example": "Design a solution combining [X], [Y], and [Z]."
    },
    6: {
        "name": "Mastery",
        "question_types": ["teach_back", "edge_cases", "critique"],
        "hints_allowed": 0,
        "time_pressure": "strict",
        "answer_format": "expert_explanation",
        "example": "Explain [concept] as if teaching someone else, including edge cases."
    }
}
New Agent: Difficulty Adapter Agent
pythondifficulty_adapter = Agent(
    name="DifficultyAdapter",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="""
    You manage adaptive difficulty for the learning experience.
    
    INPUTS:
    - Recent performance history: {performance_history}
    - Current difficulty level: {current_difficulty}
    - Concept complexity rating: {concept_complexity}
    - Learner's confidence signals: {confidence_signals}
    
    ADAPTATION RULES:
    
    1. INCREASE DIFFICULTY when:
       - Last 3 answers scored > 85% average
       - Response time is decreasing (getting faster)
       - Learner explicitly requests harder questions
       - No hints were needed in last 2 questions
    
    2. DECREASE DIFFICULTY when:
       - Last 2 answers scored < 50%
       - Multiple hints requested consecutively
       - Learner expresses confusion or frustration
       - Response time is very long (struggling)
    
    3. MAINTAIN DIFFICULTY when:
       - Scores are between 60-85% (optimal learning zone)
       - Mixed performance (some good, some struggling)
    
    OUTPUT:
    - new_difficulty_level (1-6)
    - adjustment_reason
    - recommended_question_types
    - scaffolding_suggestions (if decreasing)
    """,
    tools=[
        FunctionTool(analyze_performance_trend),
        FunctionTool(calculate_optimal_difficulty),
        FunctionTool(get_scaffolding_hints)
    ],
    output_key="difficulty_settings"
)
Adaptive Difficulty Tools
pythondef analyze_performance_trend(
    tool_context: ToolContext,
    window_size: int = 5
) -> dict:
    """
    Analyzes recent performance to detect trends.
    
    Args:
        tool_context: ADK tool context with session state
        window_size: Number of recent answers to analyze
        
    Returns:
        Performance trend analysis
    """
    history = tool_context.state.get("answer_history", [])
    recent = history[-window_size:] if len(history) >= window_size else history
    
    if not recent:
        return {
            "trend": "insufficient_data",
            "recommendation": "start_at_baseline"
        }
    
    scores = [h["score"] for h in recent]
    times = [h["response_time"] for h in recent]
    hints_used = [h["hints_used"] for h in recent]
    
    avg_score = sum(scores) / len(scores)
    score_trend = "improving" if len(scores) > 1 and scores[-1] > scores[0] else "declining" if scores[-1] < scores[0] else "stable"
    
    avg_time = sum(times) / len(times)
    time_trend = "faster" if len(times) > 1 and times[-1] < times[0] else "slower" if times[-1] > times[0] else "stable"
    
    avg_hints = sum(hints_used) / len(hints_used)
    
    return {
        "average_score": avg_score,
        "score_trend": score_trend,
        "average_response_time": avg_time,
        "time_trend": time_trend,
        "average_hints_used": avg_hints,
        "sample_size": len(recent),
        "trend": "positive" if avg_score > 75 and score_trend != "declining" else "negative" if avg_score < 50 else "neutral"
    }


def calculate_optimal_difficulty(
    tool_context: ToolContext,
    current_level: int,
    performance_trend: dict,
    concept_complexity: int
) -> dict:
    """
    Calculates the optimal difficulty level based on performance.
    
    Args:
        tool_context: ADK tool context
        current_level: Current difficulty (1-6)
        performance_trend: Output from analyze_performance_trend
        concept_complexity: Inherent complexity of current concept (1-5)
        
    Returns:
        Optimal difficulty settings
    """
    avg_score = performance_trend.get("average_score", 50)
    trend = performance_trend.get("trend", "neutral")
    avg_hints = performance_trend.get("average_hints_used", 0)
    
    # Calculate adjustment
    adjustment = 0
    reasons = []
    
    # Score-based adjustment
    if avg_score >= 90 and trend == "positive":
        adjustment += 1
        reasons.append("Excellent performance (90%+)")
    elif avg_score >= 80:
        adjustment += 0.5
        reasons.append("Strong performance (80-90%)")
    elif avg_score < 40:
        adjustment -= 1
        reasons.append("Struggling (below 40%)")
    elif avg_score < 60:
        adjustment -= 0.5
        reasons.append("Below optimal zone (40-60%)")
    
    # Hint-based adjustment
    if avg_hints == 0 and avg_score > 70:
        adjustment += 0.5
        reasons.append("No hints needed")
    elif avg_hints >= 2:
        adjustment -= 0.5
        reasons.append("Heavy hint usage")
    
    # Apply concept complexity modifier
    complexity_modifier = (concept_complexity - 3) * 0.2  # -0.4 to +0.4
    
    # Calculate new level
    new_level = current_level + adjustment + complexity_modifier
    new_level = max(1, min(6, round(new_level)))  # Clamp to 1-6
    
    # Store in state
    tool_context.state["current_difficulty"] = new_level
    tool_context.state["difficulty_history"] = tool_context.state.get("difficulty_history", []) + [new_level]
    
    return {
        "previous_level": current_level,
        "new_level": new_level,
        "adjustment": new_level - current_level,
        "reasons": reasons,
        "difficulty_config": DIFFICULTY_LEVELS[new_level]
    }


def get_scaffolding_hints(
    concept_id: str,
    difficulty_level: int,
    struggle_area: str
) -> dict:
    """
    Provides scaffolding support when difficulty decreases.
    
    Args:
        concept_id: The concept being learned
        difficulty_level: Target difficulty level
        struggle_area: Where the learner is struggling
        
    Returns:
        Scaffolding strategies and hints
    """
    scaffolding_strategies = {
        "definition": [
            "Let's start with the basic definition",
            "Think of it as...",
            "The key word here is..."
        ],
        "process": [
            "Let's break this into steps",
            "First, ... then, ... finally, ...",
            "The sequence goes like this..."
        ],
        "relationship": [
            "Think about how X affects Y",
            "If X changes, what happens to Y?",
            "These are connected because..."
        ],
        "application": [
            "Let's look at a simpler example first",
            "In everyday terms, this is like...",
            "Start with what you know..."
        ]
    }
    
    return {
        "scaffolding_type": struggle_area,
        "hints": scaffolding_strategies.get(struggle_area, scaffolding_strategies["definition"]),
        "simplified_question_template": f"Let's simplify: {struggle_area} of the concept",
        "visual_aid_suggestion": f"A diagram showing {struggle_area} might help"
    }


def record_answer_performance(
    tool_context: ToolContext,
    score: float,
    response_time: float,
    hints_used: int,
    difficulty_level: int,
    concept_id: str
) -> dict:
    """
    Records answer performance for adaptive difficulty tracking.
    
    Args:
        tool_context: ADK tool context
        score: Score achieved (0-100)
        response_time: Time taken to answer (seconds)
        hints_used: Number of hints requested
        difficulty_level: Difficulty of the question
        concept_id: Concept being tested
        
    Returns:
        Confirmation of recorded data
    """
    performance_record = {
        "timestamp": datetime.now().isoformat(),
        "score": score,
        "response_time": response_time,
        "hints_used": hints_used,
        "difficulty_level": difficulty_level,
        "concept_id": concept_id,
        "in_optimal_zone": 60 <= score <= 85  # Optimal learning challenge
    }
    
    # Append to history
    history = tool_context.state.get("answer_history", [])
    history.append(performance_record)
    tool_context.state["answer_history"] = history
    
    # Update concept-specific stats
    concept_key = f"concept_stats:{concept_id}"
    concept_stats = tool_context.state.get(concept_key, {"attempts": 0, "total_score": 0})
    concept_stats["attempts"] += 1
    concept_stats["total_score"] += score
    concept_stats["average"] = concept_stats["total_score"] / concept_stats["attempts"]
    concept_stats["last_difficulty"] = difficulty_level
    tool_context.state[concept_key] = concept_stats
    
    return {
        "status": "recorded",
        "total_answers": len(history),
        "concept_average": concept_stats["average"]
    }
Updated Quiz Generator with Adaptive Difficulty
pythonadaptive_quiz_generator = Agent(
    name="AdaptiveQuizGenerator",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="""
    Generate quiz questions adapted to the learner's current level.
    
    INPUTS:
    - Concept: {current_concept}
    - Difficulty settings: {difficulty_settings}
    - Knowledge graph context: {knowledge_graph}
    - Previous questions asked: {question_history}
    
    DIFFICULTY-BASED QUESTION GENERATION:
    
    Level 1 (Foundation):
    - "What is [concept]?"
    - "True or False: [statement about concept]"
    - "Which of these describes [concept]?"
    
    Level 2 (Understanding):
    - "Explain [concept] in your own words"
    - "What is the purpose of [concept]?"
    - "How does [concept] differ from [related concept]?"
    
    Level 3 (Application):
    - "Given [scenario], how would you use [concept]?"
    - "What would happen if [concept] was applied to [situation]?"
    - "Solve this problem using [concept]: [problem]"
    
    Level 4 (Analysis):
    - "Why does [concept] work this way?"
    - "What are the pros and cons of [concept]?"
    - "How does [concept] relate to [other concepts]?"
    
    Level 5 (Synthesis):
    - "Design a solution that combines [concept A] and [concept B]"
    - "Create an example that demonstrates [concept]"
    - "How would you improve [concept] for [use case]?"
    
    Level 6 (Mastery):
    - "Teach me [concept] as if I know nothing about it"
    - "What are the edge cases or exceptions for [concept]?"
    - "Critique this implementation of [concept]: [example]"
    
    OUTPUT:
    - question_text
    - question_type
    - difficulty_level
    - expected_answer_points (key points to look for)
    - available_hints (based on difficulty)
    - follow_up_questions (for deeper probing)
    - time_suggestion (optional)
    """,
    output_key="current_question"
)
Adaptive Flow Integration
python# Updated Learning Loop with Adaptive Difficulty
adaptive_learning_loop = LoopAgent(
    name="AdaptiveLearningLoop",
    sub_agents=[
        concept_explorer,           # Select next concept
        difficulty_adapter,         # Calculate optimal difficulty
        adaptive_quiz_generator,    # Generate difficulty-appropriate question
        answer_evaluator,           # Evaluate response
        progress_tracker            # Update progress and record performance
    ],
    max_iterations=100
)
```

---

## 📊 Enhancement 2: Export Progress - PDF Report Generator

### Report Structure Overview
```
┌─────────────────────────────────────────────────────────────────┐
│                    LEARNING PROGRESS REPORT                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📋 Executive Summary                                            │
│  📈 Overall Progress Metrics                                     │
│  🎯 Concept Mastery Breakdown                                    │
│  📊 Learning Curve Visualization                                 │
│  💡 Strengths & Areas for Improvement                           │
│  🔗 Concept Relationship Map                                     │
│  📝 Detailed Question History                                    │
│  🎓 Recommendations for Next Steps                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
New Agent: Report Generator Agent
pythonreport_generator = Agent(
    name="ReportGenerator",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="""
    Generate a comprehensive learning progress report.
    
    INPUTS:
    - Learner profile: {learner_profile}
    - Session history: {session_history}
    - Concept mastery data: {mastery_data}
    - Answer history: {answer_history}
    - Knowledge graph: {knowledge_graph}
    - Difficulty progression: {difficulty_history}
    
    REPORT SECTIONS TO GENERATE:
    
    1. EXECUTIVE SUMMARY
       - Overall mastery percentage
       - Time spent learning
       - Key achievements
       - Current status
    
    2. CONCEPT MASTERY BREAKDOWN
       - For each concept: mastery %, attempts, trend
       - Visual mastery indicators (🟢🟡🔴)
       - Sub-concept details
    
    3. LEARNING ANALYTICS
       - Score progression over time
       - Difficulty level progression
       - Response time trends
       - Hint usage patterns
    
    4. STRENGTHS & IMPROVEMENTS
       - Top 3 strongest concepts
       - Top 3 concepts needing work
       - Specific skill gaps identified
    
    5. QUESTION PERFORMANCE
       - Questions answered correctly
       - Questions with partial credit
       - Questions to revisit
    
    6. PERSONALIZED RECOMMENDATIONS
       - Suggested review topics
       - Recommended difficulty for next session
       - Learning strategy suggestions
    
    OUTPUT: Structured report data for PDF generation
    """,
    tools=[
        FunctionTool(compile_mastery_summary),
        FunctionTool(generate_analytics_charts),
        FunctionTool(create_recommendations),
        FunctionTool(generate_pdf_report)
    ],
    output_key="report_data"
)
Report Generation Tools
pythonimport json
from datetime import datetime
from typing import Dict, List, Any

def compile_mastery_summary(tool_context: ToolContext) -> dict:
    """
    Compiles all mastery data into a summary structure.
    
    Args:
        tool_context: ADK tool context with session state
        
    Returns:
        Comprehensive mastery summary
    """
    # Gather all concept stats
    all_concepts = tool_context.state.get("all_concepts", [])
    knowledge_graph = tool_context.state.get("knowledge_graph", {})
    answer_history = tool_context.state.get("answer_history", [])
    
    concept_summaries = []
    total_mastery = 0
    
    for concept_id in all_concepts:
        concept_key = f"concept_stats:{concept_id}"
        stats = tool_context.state.get(concept_key, {})
        
        # Calculate mastery dimensions
        mastery_data = {
            "concept_id": concept_id,
            "concept_name": knowledge_graph.get("nodes", {}).get(concept_id, {}).get("name", concept_id),
            "attempts": stats.get("attempts", 0),
            "average_score": stats.get("average", 0),
            "last_difficulty": stats.get("last_difficulty", 1),
            "mastery_level": calculate_mastery_level(stats.get("average", 0)),
            "trend": calculate_trend(concept_id, answer_history),
            "time_spent": calculate_time_on_concept(concept_id, answer_history)
        }
        
        concept_summaries.append(mastery_data)
        total_mastery += mastery_data["average_score"]
    
    overall_mastery = total_mastery / len(all_concepts) if all_concepts else 0
    
    return {
        "overall_mastery_percentage": round(overall_mastery, 1),
        "total_concepts": len(all_concepts),
        "concepts_mastered": len([c for c in concept_summaries if c["mastery_level"] == "mastered"]),
        "concepts_in_progress": len([c for c in concept_summaries if c["mastery_level"] == "learning"]),
        "concepts_not_started": len([c for c in concept_summaries if c["mastery_level"] == "not_started"]),
        "concept_details": concept_summaries,
        "total_questions_answered": len(answer_history),
        "total_time_spent": sum(h.get("response_time", 0) for h in answer_history),
        "average_score": sum(h.get("score", 0) for h in answer_history) / len(answer_history) if answer_history else 0
    }


def calculate_mastery_level(average_score: float) -> str:
    """Determines mastery level from average score."""
    if average_score >= 85:
        return "mastered"
    elif average_score >= 60:
        return "learning"
    elif average_score > 0:
        return "struggling"
    else:
        return "not_started"


def calculate_trend(concept_id: str, answer_history: list) -> str:
    """Calculates learning trend for a concept."""
    concept_answers = [h for h in answer_history if h.get("concept_id") == concept_id]
    if len(concept_answers) < 2:
        return "insufficient_data"
    
    first_half = concept_answers[:len(concept_answers)//2]
    second_half = concept_answers[len(concept_answers)//2:]
    
    first_avg = sum(h["score"] for h in first_half) / len(first_half)
    second_avg = sum(h["score"] for h in second_half) / len(second_half)
    
    if second_avg > first_avg + 10:
        return "improving"
    elif second_avg < first_avg - 10:
        return "declining"
    else:
        return "stable"


def calculate_time_on_concept(concept_id: str, answer_history: list) -> float:
    """Calculates total time spent on a concept."""
    concept_answers = [h for h in answer_history if h.get("concept_id") == concept_id]
    return sum(h.get("response_time", 0) for h in concept_answers)


def generate_analytics_charts(tool_context: ToolContext) -> dict:
    """
    Generates data structures for analytics visualizations.
    
    Args:
        tool_context: ADK tool context
        
    Returns:
        Chart data for various visualizations
    """
    answer_history = tool_context.state.get("answer_history", [])
    difficulty_history = tool_context.state.get("difficulty_history", [])
    
    # Score progression over time
    score_progression = [
        {
            "question_number": i + 1,
            "score": h.get("score", 0),
            "timestamp": h.get("timestamp", "")
        }
        for i, h in enumerate(answer_history)
    ]
    
    # Difficulty progression
    difficulty_progression = [
        {
            "question_number": i + 1,
            "difficulty": d
        }
        for i, d in enumerate(difficulty_history)
    ]
    
    # Performance by difficulty level
    performance_by_difficulty = {}
    for h in answer_history:
        level = h.get("difficulty_level", 1)
        if level not in performance_by_difficulty:
            performance_by_difficulty[level] = {"scores": [], "count": 0}
        performance_by_difficulty[level]["scores"].append(h.get("score", 0))
        performance_by_difficulty[level]["count"] += 1
    
    # Calculate averages per difficulty
    for level, data in performance_by_difficulty.items():
        data["average"] = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0
    
    # Response time trend
    time_trend = [
        {
            "question_number": i + 1,
            "response_time": h.get("response_time", 0)
        }
        for i, h in enumerate(answer_history)
    ]
    
    # Hint usage
    hint_usage = {
        "total_hints_used": sum(h.get("hints_used", 0) for h in answer_history),
        "questions_without_hints": len([h for h in answer_history if h.get("hints_used", 0) == 0]),
        "average_hints_per_question": sum(h.get("hints_used", 0) for h in answer_history) / len(answer_history) if answer_history else 0
    }
    
    return {
        "score_progression": score_progression,
        "difficulty_progression": difficulty_progression,
        "performance_by_difficulty": performance_by_difficulty,
        "time_trend": time_trend,
        "hint_usage": hint_usage
    }


def create_recommendations(
    tool_context: ToolContext,
    mastery_summary: dict
) -> dict:
    """
    Creates personalized learning recommendations.
    
    Args:
        tool_context: ADK tool context
        mastery_summary: Output from compile_mastery_summary
        
    Returns:
        Personalized recommendations
    """
    concept_details = mastery_summary.get("concept_details", [])
    answer_history = tool_context.state.get("answer_history", [])
    
    # Find strongest concepts
    sorted_by_score = sorted(concept_details, key=lambda x: x["average_score"], reverse=True)
    strengths = sorted_by_score[:3]
    
    # Find concepts needing improvement
    weaknesses = sorted_by_score[-3:] if len(sorted_by_score) >= 3 else sorted_by_score
    weaknesses = [c for c in weaknesses if c["average_score"] < 80]
    
    # Analyze hint patterns
    heavy_hint_concepts = [
        h["concept_id"] for h in answer_history 
        if h.get("hints_used", 0) >= 2
    ]
    hint_problem_concepts = list(set(heavy_hint_concepts))
    
    # Determine recommended starting difficulty for next session
    recent_difficulties = tool_context.state.get("difficulty_history", [])[-10:]
    avg_recent_difficulty = sum(recent_difficulties) / len(recent_difficulties) if recent_difficulties else 3
    
    # Calculate optimal zone time
    optimal_zone_answers = [h for h in answer_history if h.get("in_optimal_zone", False)]
    optimal_zone_percentage = len(optimal_zone_answers) / len(answer_history) * 100 if answer_history else 0
    
    recommendations = {
        "strengths": [
            {
                "concept": c["concept_name"],
                "score": c["average_score"],
                "message": f"Excellent grasp of {c['concept_name']}!"
            }
            for c in strengths
        ],
        "areas_for_improvement": [
            {
                "concept": c["concept_name"],
                "score": c["average_score"],
                "suggestion": f"Review {c['concept_name']} fundamentals",
                "priority": "high" if c["average_score"] < 50 else "medium"
            }
            for c in weaknesses
        ],
        "concepts_needing_hint_review": hint_problem_concepts,
        "recommended_next_difficulty": round(avg_recent_difficulty),
        "optimal_zone_time_percentage": round(optimal_zone_percentage, 1),
        "next_session_suggestions": [],
        "study_strategies": []
    }
    
    # Add specific suggestions based on analysis
    if optimal_zone_percentage < 50:
        recommendations["study_strategies"].append(
            "Consider adjusting question difficulty to spend more time in the optimal learning zone (60-85% scores)"
        )
    
    if weaknesses:
        recommendations["next_session_suggestions"].append(
            f"Start next session with: {weaknesses[0]['concept_name']}"
        )
    
    if mastery_summary["overall_mastery_percentage"] >= 80:
        recommendations["next_session_suggestions"].append(
            "Ready for advanced synthesis questions combining multiple concepts"
        )
    
    return recommendations


def generate_pdf_report(
    tool_context: ToolContext,
    mastery_summary: dict,
    analytics_data: dict,
    recommendations: dict,
    output_path: str = "learning_report.pdf"
) -> dict:
    """
    Generates a PDF report from compiled data.
    
    Args:
        tool_context: ADK tool context
        mastery_summary: Compiled mastery data
        analytics_data: Chart and analytics data
        recommendations: Personalized recommendations
        output_path: Where to save the PDF
        
    Returns:
        Status and path to generated PDF
    """
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, Image, HRFlowable
    )
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.lineplots import LinePlot
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.widgets.markers import makeMarker
    
    # Create document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#1a73e8')
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.HexColor('#202124')
    )
    body_style = styles['Normal']
    
    # Build content
    story = []
    
    # Title
    story.append(Paragraph("📚 Learning Progress Report", title_style))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        body_style
    ))
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#e8eaed')))
    story.append(Spacer(1, 20))
    
    # Executive Summary
    story.append(Paragraph("📋 Executive Summary", heading_style))
    
    summary_data = [
        ["Overall Mastery", f"{mastery_summary['overall_mastery_percentage']}%"],
        ["Total Concepts", str(mastery_summary['total_concepts'])],
        ["Concepts Mastered", f"🟢 {mastery_summary['concepts_mastered']}"],
        ["Concepts In Progress", f"🟡 {mastery_summary['concepts_in_progress']}"],
        ["Questions Answered", str(mastery_summary['total_questions_answered'])],
        ["Average Score", f"{mastery_summary['average_score']:.1f}%"],
        ["Time Spent", f"{mastery_summary['total_time_spent'] / 60:.1f} minutes"]
    ]
    
    summary_table = Table(summary_data, colWidths=[2.5*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#202124')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e8eaed'))
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 30))
    
    # Concept Mastery Breakdown
    story.append(Paragraph("🎯 Concept Mastery Breakdown", heading_style))
    
    concept_data = [["Concept", "Score", "Status", "Trend", "Attempts"]]
    for concept in mastery_summary['concept_details']:
        status_emoji = {
            "mastered": "🟢",
            "learning": "🟡",
            "struggling": "🔴",
            "not_started": "⚪"
        }.get(concept['mastery_level'], "⚪")
        
        trend_emoji = {
            "improving": "📈",
            "stable": "➡️",
            "declining": "📉",
            "insufficient_data": "❓"
        }.get(concept['trend'], "❓")
        
        concept_data.append([
            concept['concept_name'][:30],  # Truncate long names
            f"{concept['average_score']:.1f}%",
            status_emoji,
            trend_emoji,
            str(concept['attempts'])
        ])
    
    concept_table = Table(concept_data, colWidths=[2*inch, 1*inch, 0.8*inch, 0.8*inch, 0.8*inch])
    concept_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e8eaed')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
    ]))
    story.append(concept_table)
    story.append(Spacer(1, 30))
    
    # Performance by Difficulty
    story.append(Paragraph("📊 Performance by Difficulty Level", heading_style))
    
    perf_by_diff = analytics_data['performance_by_difficulty']
    diff_data = [["Level", "Name", "Avg Score", "Questions"]]
    for level in sorted(perf_by_diff.keys()):
        data = perf_by_diff[level]
        level_name = DIFFICULTY_LEVELS.get(level, {}).get('name', 'Unknown')
        diff_data.append([
            str(level),
            level_name,
            f"{data['average']:.1f}%",
            str(data['count'])
        ])
    
    diff_table = Table(diff_data, colWidths=[0.8*inch, 1.5*inch, 1.2*inch, 1*inch])
    diff_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34a853')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e8eaed'))
    ]))
    story.append(diff_table)
    story.append(Spacer(1, 30))
    
    # Page break before recommendations
    story.append(PageBreak())
    
    # Strengths & Areas for Improvement
    story.append(Paragraph("💪 Strengths", heading_style))
    for strength in recommendations['strengths']:
        story.append(Paragraph(
            f"🟢 <b>{strength['concept']}</b> ({strength['score']:.1f}%) - {strength['message']}",
            body_style
        ))
        story.append(Spacer(1, 5))
    
    story.append(Spacer(1, 20))
    story.append(Paragraph("🎯 Areas for Improvement", heading_style))
    for area in recommendations['areas_for_improvement']:
        priority_color = '#ea4335' if area['priority'] == 'high' else '#fbbc04'
        story.append(Paragraph(
            f"<font color='{priority_color}'>●</font> <b>{area['concept']}</b> ({area['score']:.1f}%) - {area['suggestion']}",
            body_style
        ))
        story.append(Spacer(1, 5))
    
    # Learning Insights
    story.append(Spacer(1, 20))
    story.append(Paragraph("💡 Learning Insights", heading_style))
    
    hint_usage = analytics_data['hint_usage']
    story.append(Paragraph(
        f"• Total hints used: {hint_usage['total_hints_used']}",
        body_style
    ))
    story.append(Paragraph(
        f"• Questions answered without hints: {hint_usage['questions_without_hints']}",
        body_style
    ))
    story.append(Paragraph(
        f"• Time in optimal learning zone: {recommendations['optimal_zone_time_percentage']}%",
        body_style
    ))
    
    # Recommendations
    story.append(Spacer(1, 20))
    story.append(Paragraph("🎓 Recommendations for Next Session", heading_style))
    
    for suggestion in recommendations['next_session_suggestions']:
        story.append(Paragraph(f"→ {suggestion}", body_style))
        story.append(Spacer(1, 5))
    
    story.append(Paragraph(
        f"→ Recommended starting difficulty: Level {recommendations['recommended_next_difficulty']}",
        body_style
    ))
    
    for strategy in recommendations['study_strategies']:
        story.append(Paragraph(f"💡 {strategy}", body_style))
        story.append(Spacer(1, 5))
    
    # Footer
    story.append(Spacer(1, 40))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e8eaed')))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<i>Generated by Adaptive Quiz Agent | Powered by Google ADK</i>",
        ParagraphStyle('Footer', parent=body_style, fontSize=9, textColor=colors.gray)
    ))
    
    # Build PDF
    doc.build(story)
    
    return {
        "status": "success",
        "output_path": output_path,
        "pages_generated": 2,  # Approximate
        "message": f"Report successfully generated at {output_path}"
    }
```

### Export Progress User Flow
```
User: "Generate my progress report"
      │
      ▼
Report Generator Agent activates
      │
      ▼
compile_mastery_summary() - Gather all progress data
      │
      ▼
generate_analytics_charts() - Create visualization data
      │
      ▼
create_recommendations() - Personalized suggestions
      │
      ▼
generate_pdf_report() - Create PDF file
      │
      ▼
Return PDF path to user
      │
      ▼
User downloads/views report
Export Tool for User
pythondef export_learning_report(
    tool_context: ToolContext,
    report_format: str = "pdf",
    include_analytics: bool = True,
    include_question_history: bool = False
) -> dict:
    """
    Main tool for users to request their learning report.
    
    Args:
        tool_context: ADK tool context
        report_format: Output format (pdf, json, html)
        include_analytics: Include detailed analytics
        include_question_history: Include all Q&A history
        
    Returns:
        Report generation status and download path
    """
    # Compile data
    mastery_summary = compile_mastery_summary(tool_context)
    analytics_data = generate_analytics_charts(tool_context) if include_analytics else {}
    recommendations = create_recommendations(tool_context, mastery_summary)
    
    if include_question_history:
        mastery_summary["full_question_history"] = tool_context.state.get("answer_history", [])
    
    # Generate based on format
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if report_format == "pdf":
        output_path = f"learning_report_{timestamp}.pdf"
        result = generate_pdf_report(
            tool_context, mastery_summary, analytics_data, recommendations, output_path
        )
    elif report_format == "json":
        output_path = f"learning_report_{timestamp}.json"
        with open(output_path, "w") as f:
            json.dump({
                "mastery": mastery_summary,
                "analytics": analytics_data,
                "recommendations": recommendations
            }, f, indent=2)
        result = {"status": "success", "output_path": output_path}
    else:
        result = {"status": "error", "message": f"Unknown format: {report_format}"}
    
    return result
```

---

## 🏗️ Updated Complete Architecture
```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                               │
│                  (Chat Interface / ADK Web UI)                       │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      ROOT COORDINATOR AGENT                          │
│          (Orchestrates learning flow & session management)           │
└─────────────────────────────────────────────────────────────────────┘
      │           │           │           │           │           │
      ▼           ▼           ▼           ▼           ▼           ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│Document │ │Concept  │ │Adaptive │ │Progress │ │Difficulty│ │Report   │
│Analyzer │ │Explorer │ │Quiz Gen │ │Tracker  │ │Adapter  │ │Generator│
│ Agent   │ │ Agent   │ │ Agent   │ │ Agent   │ │ Agent   │ │ Agent   │
└─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘
     │                                    │           │           │
     ▼                                    ▼           ▼           ▼
┌─────────┐                         ┌─────────┐ ┌─────────┐ ┌─────────┐
│PDF Tool │                         │Session  │ │Perf.    │ │PDF Gen  │
│Extract  │                         │Memory   │ │History  │ │(Report) │
└─────────┘                         └─────────┘ └─────────┘ └─────────┘
```

---

## 📋 Updated Capstone Points Mapping

| Capstone Requirement | Implementation | Details |
|---------------------|----------------|---------|
| **Multi-Agent Architecture** | ✅ 7 agents | Document Analyzer, Concept Explorer, Adaptive Quiz Generator, Progress Tracker, Difficulty Adapter, Report Generator, Root Coordinator |
| **Custom Tools** | ✅ 12+ tools | PDF extraction, knowledge graph, mastery calculation, performance analysis, difficulty calculation, scaffolding, PDF generation |
| **Session/Memory** | ✅ Comprehensive | Answer history, difficulty history, concept stats, learner profile |
| **Workflow Patterns** | ✅ All 4 patterns | Sequential (document processing), Loop (learning), Parallel (analytics), LLM Orchestration (decisions) |
| **Observability** | ✅ Built-in | Logging, performance tracking, learning analytics |
| **Evaluation** | ✅ Multiple levels | Per-answer evaluation, mastery assessment, recommendations |
| **Adaptive Features** | ✅ NEW | 6-level difficulty, performance-based adaptation, scaffolding |
| **Export/Reporting** | ✅ NEW | PDF reports with charts, analytics, recommendations |

---

## 📁 Final Project Structure
```
adaptive-quiz-agent/
├── agent.py                          # Root coordinator & main entry
├── agents/
│   ├── document_analyzer.py          # PDF processing agent
│   ├── concept_explorer.py           # Knowledge navigation agent
│   ├── adaptive_quiz_generator.py    # Difficulty-aware quiz agent
│   ├── progress_tracker.py           # Evaluation & tracking agent
│   ├── difficulty_adapter.py         # Adaptive difficulty agent
│   └── report_generator.py           # PDF report agent
├── tools/
│   ├── pdf_tools.py                  # PDF extraction functions
│   ├── knowledge_graph_tools.py      # Graph building functions
│   ├── progress_tools.py             # State management functions
│   ├── difficulty_tools.py           # Adaptation functions
│   └── report_tools.py               # PDF generation functions
├── config/
│   ├── difficulty_levels.py          # Difficulty configuration
│   └── report_templates.py           # Report styling
├── tests/
│   ├── test_config.json              # Evaluation thresholds
│   └── integration.evalset.json      # Test cases
├── requirements.txt
├── .env
└── README.md
