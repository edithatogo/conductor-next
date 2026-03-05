#!/usr/bin/env python3
"""
Ralph Mode 2.0 CLI - Autonomous Learning & Pattern Analysis

This script provides a bridge between the AI agent's Ralph loop and the 
Python-based iteration logger and pattern analyzer.

Usage:
    python scripts/ralph_cli.py log --track-id ID --task-id ID --iteration N --status S [--error E]
    python scripts/ralph_cli.py analyze [--track-id ID]
"""

import argparse
import sys
from pathlib import Path

# Add src to path if needed
sys.path.append(str(Path(__file__).parent.parent / "conductor-core" / "src"))

from conductor_core.config import ConfigManager
from conductor_core.ralph.iteration_logger import IterationLogger, RalphIteration
from conductor_core.ralph.pattern_analyzer import PatternAnalyzer


def main():
    parser = argparse.ArgumentParser(description="Ralph Mode 2.0 CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Log command
    log_parser = subparsers.add_parser("log", help="Log a Ralph iteration")
    log_parser.add_argument("--track-id", required=True)
    log_parser.add_argument("--task-id", required=True)
    log_parser.add_argument("--iteration", type=int, required=True)
    log_parser.add_argument("--status", choices=["SUCCESS", "FAILURE", "STUCK"], required=True)
    log_parser.add_argument("--error", help="Error message if failed")
    log_parser.add_argument("--files", nargs="*", help="Files changed")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze patterns")
    analyze_parser.add_argument("--track-id", help="Filter by track ID")

    args = parser.parse_args()

    # Check feature flag
    config_manager = ConfigManager()
    if not config_manager.is_feature_enabled("enable_ralph_loop"):
        print("[SKIP] Ralph Mode 2.0 learning is disabled in feature flags.")
        return

    logger = IterationLogger()

    if args.command == "log":
        iteration = RalphIteration(
            track_id=args.track_id,
            task_id=args.task_id,
            iteration=args.iteration,
            status=args.status,
            error_message=args.error,
            files_changed=args.files or []
        )
        # For simplicity in this CLI, we complete immediately
        iteration.complete(args.status, args.error, args.files)
        logger.log_iteration(iteration)
        print(f"[OK] Logged Ralph iteration {args.iteration} for task {args.task_id}")

    elif args.command == "analyze":
        analyzer = PatternAnalyzer(logger)
        suggestions = analyzer.suggest_improvements(args.track_id)
        
        if not suggestions:
            print("[INFO] No significant failure patterns detected yet.")
        else:
            print("\n[RALPH ANALYSIS] Suggested Improvements:")
            for s in suggestions:
                print(f" - {s}")
                
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
