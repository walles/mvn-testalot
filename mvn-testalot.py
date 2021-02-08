#!/usr/bin/env python3

"""
Syntax:
  mvn-testalot.py 10  <-- Runs "mvn test" 10 times, retaining all surefire-reports XML files
  mvn-testalot.py report target/testalot/  <-- Produces a Markdown report on stdout
"""

import sys
import enum

from typing import List, NamedTuple


class ResultKind(enum.Enum):
    PASS = enum.auto()
    FAIL = enum.auto()
    ERROR = enum.auto()


class Result(NamedTuple):
    name: str
    kind: ResultKind


def mvn_test_times(count: int) -> List[Result]:
    pass


def collect_results(paths: List[str]) -> List[Result]:
    pass


def print_report(results: List[Result]) -> None:
    pass


def main(args: List[str]) -> None:
    count = None
    try:
        count = int(int(args[1]))
    except:
        # Didn't work, never mind
        pass

    if count:
        results = mvn_test_times(count)
        print_report(results)
        sys.exit(0)

    assert args[1] == "report"

    # Collect test results for the given path(s)
    results = collect_results(args[2:])
    print_report(results)


if __name__ == "__main__":
    main(sys.argv)
