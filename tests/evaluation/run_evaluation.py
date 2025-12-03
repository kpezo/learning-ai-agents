#!/usr/bin/env python3
"""Evaluation runner for testing agent behavior against predefined scenarios.

This script loads evaluation scenarios from JSON files and runs them against
the educational agent system, reporting pass/fail results.

Usage:
    python tests/evaluation/run_evaluation.py --agent tutor
    python tests/evaluation/run_evaluation.py --agent assessor --verbose
    python tests/evaluation/run_evaluation.py --threshold 0.9
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

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


def run_scenario(scenario: Dict[str, Any], agent_name: str, verbose: bool = False) -> Dict[str, Any]:
    """
    Run a single evaluation scenario.

    Note: This is a stub implementation. In production, this would:
    1. Initialize ADK agent with specified name
    2. Set up session state from scenario['setup'] if provided
    3. Send scenario['input'] to agent
    4. Capture response and tool calls
    5. Match response against expected_patterns
    6. Verify required_tool_calls were made
    7. Check response_time against max_response_time_ms

    Returns:
        Dictionary with scenario results
    """
    scenario_id = scenario["scenario_id"]

    if verbose:
        print(f"\n{Colors.OKCYAN}Running scenario: {scenario_id}{Colors.ENDC}")
        print(f"  Input: {scenario['input']}")

    # Stub response for demonstration (in real implementation, call agent)
    # This allows the evaluation framework to be tested before full agent integration
    mock_response = f"This is a mock response for {scenario['input']}. " \
                    f"It mentions {agent_name} concepts relevant to the query."

    # Match patterns
    expected_patterns = scenario.get("expected_patterns", [])
    matched_count, total_patterns, matched, missing = match_patterns(mock_response, expected_patterns)

    # Calculate pass threshold
    pass_threshold = scenario.get("pass_threshold", 0.8)
    pattern_ratio = matched_count / total_patterns if total_patterns > 0 else 0
    passed = pattern_ratio >= pass_threshold

    result = {
        "scenario_id": scenario_id,
        "passed": passed,
        "response": mock_response,
        "matched_patterns": matched,
        "missing_patterns": missing,
        "pattern_match_ratio": pattern_ratio,
        "pass_threshold": pass_threshold,
        "response_time_ms": 150,  # Mock timing
    }

    if verbose:
        print(f"  Response: {mock_response[:100]}...")
        print(f"  Matched {matched_count}/{total_patterns} patterns ({pattern_ratio:.1%})")
        if missing:
            print(f"  {Colors.WARNING}Missing patterns: {missing}{Colors.ENDC}")

    return result


def run_evalset(evalset_path: Path, verbose: bool = False, threshold_override: Optional[float] = None) -> bool:
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

    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}Evaluation Set: {evalset['name']} v{evalset['version']}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}Agent: {agent_name}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")

    scenarios = evalset["scenarios"]
    results = []

    for scenario in scenarios:
        result = run_scenario(scenario, agent_name, verbose)
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

    args = parser.parse_args()

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

        passed = run_evalset(evalset_file, args.verbose, args.threshold)
        if not passed:
            all_passed = False

    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
