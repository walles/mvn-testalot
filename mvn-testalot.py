#!/usr/bin/env python3

"""
Syntax:
  mvn-testalot.py 10  <-- Runs "mvn test" 10 times, retaining all surefire-reports XML files
  mvn-testalot.py report target/testalot/  <-- Produces a Markdown report on stdout
"""

import os
import re
import sys
import enum
import shutil
import pathlib
import datetime
import subprocess

from typing import List, NamedTuple, Dict


# Number of entries to show in the slow-tests top list
TOP_SLOW_TESTS = 10


# Example: <testcase name="aclExcudeSingleCommand" classname="redis.clients.jedis.tests.commands.AccessControlListCommandsTest" time="0"/>
TESTCASE = re.compile(r'  <testcase name="([^"]+)" classname="([^"]+)" time="([^"]+)"')

# Example: <error message="ERR unknown command `ZMSCORE`, with args beginning with: `foo`, `b`, ...
ERROR = re.compile(r"    <error ")

# Example: <failure message="expected:&lt;4&gt; but was:&lt;3&gt;" type=...
FAILURE = re.compile(r"    <failure ")

# Example: target/testalot/surefire-reports-20210209T114442-3/TEST-com.spotify.ads.adserver.faf.FafQueryBuilderTest.xml
# Capture: 20210209T114442
TESTRUN_RE = re.compile(r".*/surefire-reports-([0-9T]+)(-[0-9]+)?/")


class ResultKind(enum.Enum):
    PASS = enum.auto()
    FAIL = enum.auto()
    ERROR = enum.auto()


class Result(NamedTuple):
    # Format: a.b.c.ClassName.testName()
    name: str

    kind: ResultKind
    duration: datetime.timedelta
    timestamp: datetime.datetime

    # File name with full path of the (XML) file where this test result was read from.
    path: str


def surefire_reports() -> List[str]:
    """
    Find all directories named "target/surefire-reports" next to a "pom.xml" file.
    """
    surefire_reports = []
    for dirpath, dirnames, filenames in os.walk("."):
        for filename in filenames:
            if filename != "pom.xml":
                continue

            surefire_reports_dir = os.path.join(dirpath, "target", "surefire-reports")
            if os.path.isdir(surefire_reports_dir):
                surefire_reports.append(surefire_reports_dir)

    return surefire_reports


def mvn_test_times(count: int) -> List[Result]:
    global_start = datetime.datetime.now()
    for i in range(count):
        if not os.path.isfile("pom.xml"):
            sys.exit("Must be in the root of the source tree, pom.xml not found")

        for surefire_reports_dir in surefire_reports():
            shutil.rmtree(surefire_reports_dir)

        start = datetime.datetime.now()

        # --fail-never makes all tests run in a multi module project, even if
        # earlier modules see test failures.
        result = subprocess.run(args=["mvn", "--fail-never", "test"])

        end = datetime.datetime.now()
        duration = end - start
        print("")
        print(f"mvn-testalot: Exit code {result.returncode} after {duration}")

        assert surefire_reports()  # Otherwise no tests were run

        os.makedirs("target/testalot", exist_ok=True)

        # Example: "20210208T093519"
        timestamp = (
            datetime.datetime.now()
            .isoformat(timespec="seconds")
            .replace(":", "")
            .replace("-", "")
        )

        number = 1
        for surefire_report in surefire_reports():
            shutil.move(
                surefire_report,
                f"target/testalot/surefire-reports-{timestamp}-{number}",
            )
            number += 1

        runs_left = count - 1 - i
        if runs_left:
            runs_done = i + 1
            now = datetime.datetime.now()
            time_elapsed = now - global_start
            time_per_run = time_elapsed / runs_done
            time_left = time_per_run * runs_left
            eta = now + time_left
            print(
                f"mvn-testalot: {runs_left} runs left, expect finish at {eta.isoformat(timespec='seconds')}, {time_left} from now"
            )

    now = datetime.datetime.now()
    print(f"mvn-testalot: All done at {now.isoformat(timespec='seconds')}")

    return collect_results(["target/testalot"])


def parse_xml(path: str):
    results: List[Result] = []
    current_test = None
    result_kind = None
    duration = None

    stat_result = pathlib.Path(path).stat()
    timestamp = datetime.datetime.fromtimestamp(
        stat_result.st_mtime, tz=datetime.timezone.utc
    )

    for line in open(path, "r"):
        if match := TESTCASE.match(line):
            if current_test:
                assert result_kind
                assert timestamp
                assert duration is not None
                results.append(
                    Result(current_test, result_kind, duration, timestamp, path)
                )
            testname = match.group(1)
            classname = match.group(2)
            duration = datetime.timedelta(
                # Removing the "," to be able to handle "1,234.567" style numbers
                seconds=float(match.group(3).replace(",", ""))
            )
            current_test = classname + "." + testname + "()"
            result_kind = ResultKind.PASS
            continue

        if ERROR.match(line):
            assert result_kind == ResultKind.PASS
            result_kind = ResultKind.ERROR
        elif FAILURE.match(line):
            assert result_kind == ResultKind.PASS
            result_kind = ResultKind.FAIL

        # Unknown line, just ignore it

    if current_test:
        assert timestamp
        assert result_kind
        assert duration is not None
        results.append(Result(current_test, result_kind, duration, timestamp, path))

    return results


def collect_results(paths: List[str]) -> List[Result]:
    results = []
    for path in paths:
        if os.path.isfile(path):
            if path.endswith(".xml"):
                results += parse_xml(path)
                continue

        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                file_with_path = os.path.join(dirpath, filename)
                if not file_with_path.endswith(".xml"):
                    continue

                results += parse_xml(file_with_path)

    return results


def print_slow_tests_report(results: List[Result]) -> None:
    slow_results: Dict[str, Result] = {}
    fast_results: Dict[str, Result] = {}

    # Figure out max duration for each test case
    for current_result in results:
        slow_result = slow_results.get(current_result.name, None)
        if slow_result is None or current_result.duration > slow_result.duration:
            slow_result = current_result
        slow_results[current_result.name] = slow_result

        fast_result = fast_results.get(current_result.name, None)
        if fast_result is None or current_result.duration < fast_result.duration:
            fast_result = current_result
        fast_results[current_result.name] = fast_result

    print_these = sorted(slow_results.values(), key=lambda r: r.duration, reverse=True)[
        :TOP_SLOW_TESTS
    ]

    slow_testnames = list(map(lambda result: result.name, print_these))
    total_time = datetime.timedelta(0)
    time_spent_in_slow_tests = datetime.timedelta(0)
    for current_result in results:
        total_time += current_result.duration
        if current_result.name in slow_testnames:
            time_spent_in_slow_tests += current_result.duration

    slow_test_percentage = int((time_spent_in_slow_tests * 100) / total_time)

    print("")
    print("# Slow tests")
    print("")
    print(
        f"The tests listed here make up {slow_test_percentage}% of the total testing time."
    )
    print("")
    print("Numbers in parentheses show the fastest run of each test.")
    print("")
    print("| Result |    Duration   | Name |")
    print("|--------|---------------|------|")
    for result in print_these:
        slow_duration_s = f"{result.duration.total_seconds():.1f}s"
        fast_duration_s = f"{fast_results[result.name].duration.total_seconds():.1f}s"
        duration_s = f"{slow_duration_s:>6s} ({fast_duration_s})"
        print(f"| {result.kind.name:6s} | {duration_s} | `{result.name}` |")


def is_flaky(string: str) -> bool:
    if not string:
        return False

    first_char = string[0]
    for char in string:
        if char != first_char:
            # Multiple kinds of results, we have a flake!
            return True

    return False


def count_runs(results: List[Result]) -> int:
    timestamps = set()
    for result in results:
        # Example: target/testalot/surefire-reports-20210209T114442-1/TEST-com.spotify.ads.adserver.faf.FafQueryBuilderTest.xml
        timestamp_match = TESTRUN_RE.match(result.path)
        if not timestamp_match:
            print(result.path, file=sys.stderr)
            assert timestamp_match
        timestamps.add(timestamp_match.group(1))

    return len(timestamps)


def print_flaky_tests_report(results: List[Result]) -> None:
    result_strings: Dict[str, str] = {}
    for result in sorted(results, key=lambda r: r.timestamp):
        string = result_strings.get(result.name, "")
        if result.kind == ResultKind.PASS:
            string += "."
        elif result.kind == ResultKind.FAIL:
            string += "x"
        elif result.kind == ResultKind.ERROR:
            string += "E"
        else:
            assert False
        result_strings[result.name] = string

    flakies = {}
    for name, string in result_strings.items():
        if is_flaky(string):
            flakies[name] = string

    print("")
    print(f"# Flaky tests, {count_runs(results)} runs")
    print("")

    if not flakies:
        print("No flaky tests found.")
        return

    print("`.` = pass, `x` = fail, `E` = error")
    print("")
    print("| Result | Name |")
    print("|--------|------|")
    for name in sorted(flakies.keys()):
        string = result_strings[name]
        print(f"| `{string}` | `{name}` |")


def print_report(results: List[Result]) -> None:
    print_slow_tests_report(results)
    print_flaky_tests_report(results)


def main(args: List[str]) -> None:
    count = None
    try:
        count = int(args[1])
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
