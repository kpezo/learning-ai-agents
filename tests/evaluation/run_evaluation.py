#!/usr/bin/env python3
"""Evaluation runner for testing agent behavior against predefined scenarios.

This script loads evaluation scenarios from JSON files and runs them against
the educational agent system, reporting pass/fail results.

Usage:
    python tests/evaluation/run_evaluation.py --agent tutor
    python tests/evaluation/run_evaluation.py --agent assessor --verbose
    python tests/evaluation/run_evaluation.py --threshold 0.9
    python tests/evaluation/run_evaluation.py --mock  # Force mock mode (no API calls)
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Check if real LLM is available
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
USE_REAL_LLM = bool(GOOGLE_API_KEY)

# Try to import Google GenAI for real LLM calls
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    USE_REAL_LLM = False

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def load_evalset(filepath: Path) -> Dict[str, Any]:
    """Load evaluation set from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def validate_evalset(evalset: Dict[str, Any]) -> bool:
    """Validate evaluation set has required fields."""
    required = ["name", "version", "agent", "scenarios"]
    for field in required:
        if field not in evalset:
            print(f"{Colors.FAIL}Error: Missing required field '{field}'{Colors.ENDC}")
            return False

    if not evalset["scenarios"]:
        print(f"{Colors.FAIL}Error: No scenarios found{Colors.ENDC}")
        return False

    return True


def match_patterns(text: str, patterns: List[str]) -> tuple[int, int, List[str], List[str]]:
    """
    Match patterns against text using regex.

    Returns:
        (matched_count, total_patterns, matched_patterns, missing_patterns)
    """
    matched = []
    missing = []

    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            matched.append(pattern)
        else:
            missing.append(pattern)

    return len(matched), len(patterns), matched, missing


def get_agent_system_prompt(agent_name: str) -> str:
    """Get the system prompt for a specific agent type."""
    prompts = {
        "tutor": """You are an educational tutor agent. Your role is to:
- Help students learn programming concepts
- Provide clear explanations with examples
- Guide students through problems step-by-step
- Adapt your explanations to the student's level
- Be encouraging and supportive""",
        "assessor": """You are an assessment agent. Your role is to:
- Evaluate student understanding through questions
- Provide constructive feedback on answers
- Identify areas where students need more practice
- Grade responses fairly and explain scoring""",
        "curriculum_planner": """You are a curriculum planning agent. Your role is to:
- Create personalized learning paths
- Recommend topics based on student progress
- Identify prerequisite knowledge gaps
- Suggest appropriate difficulty levels"""
    }
    return prompts.get(agent_name, prompts["tutor"])


def call_real_llm(prompt: str, agent_name: str) -> tuple[str, int]:
    """
    Call the real Google Gemini API.

    Returns:
        Tuple of (response_text, response_time_ms)
    """
    client = genai.Client(api_key=GOOGLE_API_KEY)

    system_prompt = get_agent_system_prompt(agent_name)

    start_time = time.time()

    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.7,
            max_output_tokens=1024,
        )
    )

    response_time_ms = int((time.time() - start_time) * 1000)
    response_text = response.text if response.text else ""

    return response_text, response_time_ms


def run_scenario(scenario: Dict[str, Any], agent_name: str, verbose: bool = False, use_mock: bool = False) -> Dict[str, Any]:
    """
    Run a single evaluation scenario.

    When GOOGLE_API_KEY is set and --mock is not used:
    1. Calls real Google Gemini API with agent-specific system prompt
    2. Measures actual response time
    3. Matches response against expected_patterns

    In mock mode (no API key or --mock flag):
    - Uses stub responses for testing the evaluation framework

    Returns:
        Dictionary with scenario results
    """
    scenario_id = scenario["scenario_id"]

    if verbose:
        print(f"\n{Colors.OKCYAN}Running scenario: {scenario_id}{Colors.ENDC}")
        print(f"  Input: {scenario['input']}")

    # Determine whether to use real LLM
    use_real = USE_REAL_LLM and GENAI_AVAILABLE and not use_mock

    if use_real:
        try:
            response_text, response_time_ms = call_real_llm(scenario['input'], agent_name)
            if verbose:
                print(f"  {Colors.OKBLUE}[Real LLM]{Colors.ENDC}")
        except Exception as e:
            if verbose:
                print(f"  {Colors.WARNING}LLM call failed: {e}, falling back to mock{Colors.ENDC}")
            response_text = f"This is a mock response for {scenario['input']}. " \
                           f"It mentions {agent_name} concepts relevant to the query."
            response_time_ms = 150
    else:
        # Mock response for testing framework without API calls
        response_text = f"This is a mock response for {scenario['input']}. " \
                       f"It mentions {agent_name} concepts relevant to the query."
        response_time_ms = 150
        if verbose:
            print(f"  {Colors.WARNING}[Mock Mode]{Colors.ENDC}")

    # Match patterns
    expected_patterns = scenario.get("expected_patterns", [])
    matched_count, total_patterns, matched, missing = match_patterns(response_text, expected_patterns)

    # Calculate pass threshold
    pass_threshold = scenario.get("pass_threshold", 0.8)
    pattern_ratio = matched_count / total_patterns if total_patterns > 0 else 0
    passed = pattern_ratio >= pass_threshold

    result = {
        "scenario_id": scenario_id,
        "passed": passed,
        "response": response_text,
        "matched_patterns": matched,
        "missing_patterns": missing,
        "pattern_match_ratio": pattern_ratio,
        "pass_threshold": pass_threshold,
        "response_time_ms": response_time_ms,
        "used_real_llm": use_real,
    }

    if verbose:
        print(f"  Response: {response_text[:150]}...")
        print(f"  Matched {matched_count}/{total_patterns} patterns ({pattern_ratio:.1%})")
        print(f"  Response time: {response_time_ms}ms")
        if missing:
            print(f"  {Colors.WARNING}Missing patterns: {missing}{Colors.ENDC}")

    return result


def run_evalset(evalset_path: Path, verbose: bool = False, threshold_override: Optional[float] = None, use_mock: bool = False) -> bool:
    """
    Run all scenarios in an evaluation set.

    Returns:
        True if evalset passes, False otherwise
    """
    evalset = load_evalset(evalset_path)

    if not validate_evalset(evalset):
        return False

    agent_name = evalset["agent"]
    pass_threshold = threshold_override if threshold_override is not None else evalset.get("pass_threshold", 0.8)

    # Determine LLM mode
    llm_mode = "Mock" if use_mock or not USE_REAL_LLM else "Real LLM (Gemini)"

    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}Evaluation Set: {evalset['name']} v{evalset['version']}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}Agent: {agent_name}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}Mode: {llm_mode}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")

    scenarios = evalset["scenarios"]
    results = []

    for scenario in scenarios:
        result = run_scenario(scenario, agent_name, verbose, use_mock)
        results.append(result)

        # Print individual scenario result
        status = f"{Colors.OKGREEN}PASS{Colors.ENDC}" if result["passed"] else f"{Colors.FAIL}FAIL{Colors.ENDC}"
        print(f"  [{status}] {result['scenario_id']}")

    # Calculate aggregate results
    passed_count = sum(1 for r in results if r["passed"])
    total_count = len(results)
    pass_rate = passed_count / total_count if total_count > 0 else 0

    evalset_passed = pass_rate >= pass_threshold

    # Print summary
    print(f"\n{Colors.BOLD}Results Summary:{Colors.ENDC}")
    print(f"  Scenarios passed: {passed_count}/{total_count} ({pass_rate:.1%})")
    print(f"  Pass threshold: {pass_threshold:.1%}")

    if evalset_passed:
        print(f"  {Colors.OKGREEN}{Colors.BOLD}✓ EVALUATION PASSED{Colors.ENDC}")
    else:
        print(f"  {Colors.FAIL}{Colors.BOLD}✗ EVALUATION FAILED{Colors.ENDC}")

    return evalset_passed


def main():
    """Main entry point for evaluation runner."""
    parser = argparse.ArgumentParser(description="Run agent behavior evaluations")
    parser.add_argument(
        "--agent",
        choices=["tutor", "assessor", "curriculum_planner", "all"],
        default="all",
        help="Which agent to evaluate"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output for each scenario"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        help="Override pass threshold (0.0-1.0)"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Force mock mode (no real LLM API calls)"
    )

    args = parser.parse_args()

    # Print LLM availability info
    if args.verbose:
        print(f"{Colors.OKCYAN}LLM Configuration:{Colors.ENDC}")
        print(f"  GOOGLE_API_KEY set: {bool(GOOGLE_API_KEY)}")
        print(f"  GenAI available: {GENAI_AVAILABLE}")
        print(f"  Mock mode forced: {args.mock}")
        print(f"  Will use real LLM: {USE_REAL_LLM and GENAI_AVAILABLE and not args.mock}")

    # Find evalsets directory
    evalsets_dir = Path(__file__).parent / "evalsets"

    if not evalsets_dir.exists():
        print(f"{Colors.FAIL}Error: Evalsets directory not found: {evalsets_dir}{Colors.ENDC}")
        sys.exit(1)

    # Determine which evalsets to run
    if args.agent == "all":
        evalset_files = list(evalsets_dir.glob("*_scenarios.json"))
    else:
        evalset_files = [evalsets_dir / f"{args.agent}_scenarios.json"]

    if not evalset_files:
        print(f"{Colors.FAIL}Error: No evalset files found for agent '{args.agent}'{Colors.ENDC}")
        sys.exit(1)

    # Run evaluations
    all_passed = True
    for evalset_file in evalset_files:
        if not evalset_file.exists():
            print(f"{Colors.WARNING}Warning: Evalset file not found: {evalset_file}{Colors.ENDC}")
            continue

        passed = run_evalset(evalset_file, args.verbose, args.threshold, args.mock)
        if not passed:
            all_passed = False

    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
