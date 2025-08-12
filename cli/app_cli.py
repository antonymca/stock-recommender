#!/usr/bin/env python3
"""Simple CLI wrapper for automation tools."""
import argparse

from automation.runner import run_once
from automation.schedule import main as schedule_main


def main():
    parser = argparse.ArgumentParser(description="Stock Recommender CLI")
    sub = parser.add_subparsers(dest="cmd")

    watch = sub.add_parser("sell-watch", help="Monitor positions and notify when to sell")
    watch.add_argument(
        "--positions", type=str, default="automation/positions.yaml", help="YAML file of positions"
    )
    group = watch.add_mutually_exclusive_group()
    group.add_argument("--once", action="store_true", help="Run a single evaluation")
    group.add_argument("--schedule", action="store_true", help="Run scheduler during market hours")

    args = parser.parse_args()
    if args.cmd == "sell-watch":
        if args.schedule:
            schedule_main()
        else:
            run_once(args.positions)
    else:
        parser.print_help()


if __name__ == "__main__":  # pragma: no cover
    main()
