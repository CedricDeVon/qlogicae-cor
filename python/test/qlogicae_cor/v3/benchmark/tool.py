
from __future__ import annotations

import argparse
import ast
import datetime
import importlib.metadata
import json
import os
import platform
import random
import re
import statistics
import subprocess
import sys
import time

from pathlib import Path
from typing import Any


JSON_MARKER = "__QLOGICAE_BENCHMARK_JSON__"
PROFILE_MARKER = "__QLOGICAE_IMPORT_PROFILE_START__"
REPORT_SCHEMA_VERSION = 2


WORKER_SCRIPT = r'''
from __future__ import annotations

import sys


JSON_MARKER = "__QLOGICAE_BENCHMARK_JSON__"
PROFILE_MARKER = "__QLOGICAE_IMPORT_PROFILE_START__"


def emit(result):
    print(JSON_MARKER + repr(result), flush=True)


def import_target(target):
    return __import__(target, fromlist=("__name__",))


def prepare_target(target, incremental, package_name):
    if incremental:
        import_target(package_name)

    return target in sys.modules


def current_rss():
    if sys.platform == "linux":
        import os

        try:
            with open("/proc/self/statm", encoding="utf-8") as file:
                resident_pages = int(file.read().split()[1])

            return resident_pages * os.sysconf("SC_PAGE_SIZE")

        except (OSError, ValueError, IndexError):
            return None

    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes

        try:
            class Counters(ctypes.Structure):
                _fields_ = [
                    ("cb", wintypes.DWORD),
                    ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t),
                ]

            counters = Counters()
            counters.cb = ctypes.sizeof(counters)

            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            psapi = ctypes.WinDLL("psapi", use_last_error=True)

            kernel32.GetCurrentProcess.restype = wintypes.HANDLE

            psapi.GetProcessMemoryInfo.argtypes = [
                wintypes.HANDLE,
                ctypes.POINTER(Counters),
                wintypes.DWORD,
            ]
            psapi.GetProcessMemoryInfo.restype = wintypes.BOOL

            process = kernel32.GetCurrentProcess()

            if psapi.GetProcessMemoryInfo(
                process,
                ctypes.byref(counters),
                counters.cb,
            ):
                return counters.WorkingSetSize

        except (AttributeError, OSError):
            return None

    return None


def discover(target):
    package = import_target(target)

    if not hasattr(package, "__path__"):
        raise TypeError(
            f"Target is not a package: {target}"
        )

    import pkgutil
    import time
    import tracemalloc

    tracemalloc.start()

    before, _ = tracemalloc.get_traced_memory()
    tracemalloc.reset_peak()

    start = time.perf_counter()

    module_details = []

    for info in pkgutil.walk_packages(
        package.__path__,
        prefix=package.__name__ + ".",
    ):
        origin = None
        finder = info.module_finder
        find_spec = getattr(finder, "find_spec", None)

        if callable(find_spec):
            try:
                spec = find_spec(info.name)

                if spec is not None:
                    origin = spec.origin

            except (ImportError, AttributeError, OSError, ValueError):
                pass

        module_details.append({
            "name": info.name,
            "is_package": info.ispkg,
            "origin": origin,
        })

    runtime_ms = (time.perf_counter() - start) * 1000

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    emit({
        "modules": [item["name"] for item in module_details],
        "module_details": module_details,
        "package_origin": getattr(package, "__file__", None),
        "package_paths": [
            str(path)
            for path in package.__path__
        ],
        "runtime_ms": runtime_ms,
        "retained_allocation_delta_bytes": current - before,
        "peak_allocation_delta_bytes": max(0, peak - before),
    })


def measure_runtime(target, incremental, package_name):
    import time

    already_loaded = prepare_target(
        target,
        incremental,
        package_name,
    )

    start = time.perf_counter()
    import_target(target)
    runtime_ms = (time.perf_counter() - start) * 1000

    emit({
        "runtime_ms": runtime_ms,
        "already_loaded": already_loaded,
    })


def measure_memory(target, incremental, package_name):
    already_loaded = prepare_target(
        target,
        incremental,
        package_name,
    )

    import tracemalloc

    tracemalloc.start()

    before, _ = tracemalloc.get_traced_memory()
    tracemalloc.reset_peak()

    import_target(target)

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    emit({
        "retained_allocation_delta_bytes": current - before,
        "peak_allocation_delta_bytes": max(0, peak - before),
        "already_loaded": already_loaded,
    })


def measure_rss(target, incremental, package_name):
    already_loaded = prepare_target(
        target,
        incremental,
        package_name,
    )

    before = current_rss()
    import_target(target)
    after = current_rss()

    emit({
        "rss_before_bytes": before,
        "rss_after_bytes": after,
        "already_loaded": already_loaded,
    })


def profile_imports(target):
    before = set(sys.modules)

    print(PROFILE_MARKER, file=sys.stderr, flush=True)

    import_target(target)

    loaded = sorted(set(sys.modules) - before)

    emit({
        "target": target,
        "newly_loaded_modules": loaded,
    })


mode = sys.argv[1]
target = sys.argv[2]
package_name = sys.argv[3]
incremental = len(sys.argv) > 4 and sys.argv[4] == "incremental"

if mode == "discover":
    discover(target)
elif mode == "runtime":
    measure_runtime(target, incremental, package_name)
elif mode == "memory":
    measure_memory(target, incremental, package_name)
elif mode == "rss":
    measure_rss(target, incremental, package_name)
elif mode == "profile":
    profile_imports(target)
else:
    raise ValueError(f"Unsupported benchmark mode: {mode}")
'''

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Isolated Python package import benchmark."
    )

    parser.add_argument(
        "package_paths",
        nargs="+",
        help="One or more dotted Python package import paths.",
    )

    parser.add_argument(
        "--preset",
        choices=("quick", "full"),
        default="full",
        help="Benchmark preset (default: full).",
    )

    parser.add_argument(
        "-n",
        "--repetitions",
        type=int,
        default=None,
        help="Number of repetitions. Overrides the preset default.",
    )

    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("benchmark-results.json"),
        help="JSON output path.",
    )

    parser.add_argument(
        "--no-incremental",
        action="store_true",
        help="Skip package-root-initialized import measurements.",
    )

    profile_group = parser.add_mutually_exclusive_group()

    profile_group.add_argument(
        "--import-profiles",
        dest="import_profiles",
        action="store_true",
        help="Enable import-time profiling.",
    )

    profile_group.add_argument(
        "--no-import-profiles",
        dest="import_profiles",
        action="store_false",
        help="Disable import-time profiling.",
    )

    parser.set_defaults(import_profiles=None)

    parser.add_argument(
        "--profile-limit",
        type=int,
        default=1,
        help="Number of aggregated dependencies to display.",
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Worker process timeout in seconds (default: 30).",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Seed for reproducible module-order randomization.",
    )

    parser.add_argument(
        "--python-path",
        type=Path,
        action="append",
        default=[],
        help=(
            "Additional Python import directory. "
            "Can be specified multiple times."
        ),
    )

    arguments = parser.parse_args()

    if arguments.repetitions is None:
        arguments.repetitions = (
            3 if arguments.preset == "quick" else 10
        )

    if arguments.import_profiles is None:
        arguments.import_profiles = arguments.preset == "full"

    if len(set(arguments.package_paths)) != len(arguments.package_paths):
        parser.error("Package paths must be unique.")

    return arguments


def summarize_values(
    values: list[float],
) -> dict[str, float | None]:
    if not values:
        return {
            "median": None,
            "min": None,
            "max": None,
            "stdev": None,
        }

    return {
        "median": statistics.median(values),
        "min": min(values),
        "max": max(values),
        "stdev": (
            statistics.stdev(values)
            if len(values) > 1
            else 0.0
        ),
    }


def summarize(
    results: list[dict[str, Any]],
    key: str,
) -> dict[str, float | None]:
    values = [
        float(result[key])
        for result in results
        if result.get(key) is not None
    ]

    return summarize_values(values)


def build_worker_environment(
    arguments: argparse.Namespace,
) -> tuple[dict[str, str], list[str]]:
    environment = os.environ.copy()

    paths: list[str] = []

    candidates = [
        Path.cwd(),
        Path(__file__).resolve().parent,
        *arguments.python_path,
    ]

    for candidate in candidates:
        resolved = candidate.expanduser().resolve()

        if not resolved.is_dir():
            raise ValueError(
                f"Python import path is not a directory: {resolved}"
            )

        value = str(resolved)

        if value not in paths:
            paths.append(value)

    existing = environment.get("PYTHONPATH")

    if existing:
        for value in existing.split(os.pathsep):
            if value and value not in paths:
                paths.append(value)

    environment["PYTHONPATH"] = os.pathsep.join(paths)

    return environment, paths


def run_worker(
    mode: str,
    target: str,
    package_name: str,
    environment: dict[str, str],
    timeout: float,
    incremental: bool = False,
    importtime: bool = False,
) -> tuple[dict[str, Any], str]:
    command = [sys.executable]

    if importtime:
        command.extend(["-X", "importtime"])

    command.extend([
        "-c",
        WORKER_SCRIPT,
        mode,
        target,
        package_name,
    ])

    if incremental:
        command.append("incremental")

    try:
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=timeout,
            env=environment,
        )

    except subprocess.TimeoutExpired as error:
        raise RuntimeError(
            f"Worker timed out after {timeout:.1f} seconds: "
            f"{target} ({mode})"
        ) from error

    if process.returncode != 0:
        raise RuntimeError(
            f"Benchmark failed: {target} ({mode})\n"
            f"Exit code: {process.returncode}\n"
            f"Stdout:\n{process.stdout}\n"
            f"Stderr:\n{process.stderr}"
        )

    for line in reversed(process.stdout.splitlines()):
        if line.startswith(JSON_MARKER):
            try:
                result = ast.literal_eval(
                    line[len(JSON_MARKER):]
                )

            except (ValueError, SyntaxError) as error:
                raise RuntimeError(
                    f"Invalid worker result: {target} ({mode})"
                ) from error

            if not isinstance(result, dict):
                raise RuntimeError(
                    f"Unexpected worker result: {target} ({mode})"
                )

            return result, process.stderr

    raise RuntimeError(
        f"Worker returned no result: {target} ({mode})\n"
        f"Stdout:\n{process.stdout}\n"
        f"Stderr:\n{process.stderr}"
    )


def run_repetitions(
    mode: str,
    target: str,
    package_name: str,
    repetitions: int,
    environment: dict[str, str],
    timeout: float,
) -> list[dict[str, Any]]:
    return [
        run_worker(
            mode,
            target,
            package_name,
            environment,
            timeout,
        )[0]
        for _ in range(repetitions)
    ]


def measure_imports(
    targets: list[str],
    repetitions: int,
    package_name: str,
    environment: dict[str, str],
    timeout: float,
    incremental: bool,
    seed: int,
) -> list[dict[str, Any]]:
    samples: dict[str, dict[str, Any]] = {
        target: {
            "runtime": [],
            "memory": [],
            "rss": [],
            "errors": [],
        }
        for target in targets
    }

    generator = random.Random(seed)

    for _ in range(repetitions):
        ordered_targets = list(targets)
        generator.shuffle(ordered_targets)

        for target in ordered_targets:
            for mode in ("runtime", "memory", "rss"):
                try:
                    result, _ = run_worker(
                        mode,
                        target,
                        package_name,
                        environment,
                        timeout,
                        incremental=incremental,
                    )

                    samples[target][mode].append(result)

                except RuntimeError as error:
                    samples[target]["errors"].append({
                        "mode": mode,
                        "message": str(error),
                    })

    results: list[dict[str, Any]] = []

    for target in targets:
        sample = samples[target]

        runtime_results = sample["runtime"]
        memory_results = sample["memory"]
        rss_results = sample["rss"]

        rss_deltas = [
            result["rss_after_bytes"] - result["rss_before_bytes"]
            for result in rss_results
            if (
                result["rss_before_bytes"] is not None
                and result["rss_after_bytes"] is not None
            )
        ]

        loaded_values = [
            result["already_loaded"]
            for result in runtime_results
        ]

        results.append({
            "target": target,
            "mode": (
                "package_initialized"
                if incremental
                else "cold"
            ),
            "runtime_ms": summarize(
                runtime_results,
                "runtime_ms",
            ),
            "retained_allocation_delta_bytes": summarize(
                memory_results,
                "retained_allocation_delta_bytes",
            ),
            "peak_allocation_delta_bytes": summarize(
                memory_results,
                "peak_allocation_delta_bytes",
            ),
            "rss_delta_bytes": summarize_values(
                [float(value) for value in rss_deltas]
            ),
            "already_loaded": {
                "count": sum(loaded_values),
                "total": len(loaded_values),
            },
            "successful_repetitions": {
                "runtime": len(runtime_results),
                "memory": len(memory_results),
                "rss": len(rss_results),
            },
            "requested_repetitions": repetitions,
            "errors": sample["errors"],
        })

    return results


def discover_modules(
    package_name: str,
    repetitions: int,
    environment: dict[str, str],
    timeout: float,
) -> tuple[list[str], list[dict[str, Any]], dict[str, Any]]:
    results = run_repetitions(
        "discover",
        package_name,
        package_name,
        repetitions,
        environment,
        timeout,
    )

    module_sets = [
        result["modules"]
        for result in results
    ]

    if any(
        modules != module_sets[0]
        for modules in module_sets[1:]
    ):
        raise RuntimeError(
            "Package discovery returned inconsistent module lists."
        )

    module_details = results[0]["module_details"]

    return module_sets[0], module_details, {
        "module_count": len(module_sets[0]),
        "package_origin": results[0]["package_origin"],
        "package_paths": results[0]["package_paths"],
        "runtime_ms": summarize(results, "runtime_ms"),
        "retained_allocation_delta_bytes": summarize(
            results,
            "retained_allocation_delta_bytes",
        ),
        "peak_allocation_delta_bytes": summarize(
            results,
            "peak_allocation_delta_bytes",
        ),
        "repetitions": repetitions,
    }


def parse_importtime(stderr: str) -> list[dict[str, Any]]:
    if PROFILE_MARKER not in stderr:
        return []

    stderr = stderr.split(PROFILE_MARKER, 1)[1]

    pattern = re.compile(
        r"import time:\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(.+)"
    )

    results: list[dict[str, Any]] = []

    for line in stderr.splitlines():
        match = pattern.search(line)

        if match is None:
            continue

        results.append({
            "module": match.group(3).strip(),
            "self_time_us": int(match.group(1)),
            "cumulative_time_us": int(match.group(2)),
        })

    return results


def profile_imports(
    target: str,
    package_name: str,
    environment: dict[str, str],
    timeout: float,
) -> dict[str, Any]:
    try:
        result, stderr = run_worker(
            "profile",
            target,
            package_name,
            environment,
            timeout,
            importtime=True,
        )

        return {
            "target": target,
            "modules": parse_importtime(stderr),
            "newly_loaded_modules": result["newly_loaded_modules"],
            "error": None,
        }

    except RuntimeError as error:
        return {
            "target": target,
            "modules": [],
            "newly_loaded_modules": [],
            "error": str(error),
        }


def aggregate_import_profiles(
    profiles: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}

    for profile in profiles:
        for module in profile["modules"]:
            grouped.setdefault(
                module["module"],
                [],
            ).append({
                "target": profile["target"],
                "self_time_us": module["self_time_us"],
                "cumulative_time_us": module["cumulative_time_us"],
            })

    aggregated: list[dict[str, Any]] = []

    for module_name, observations in grouped.items():
        self_times = [
            float(item["self_time_us"])
            for item in observations
        ]

        cumulative_times = [
            float(item["cumulative_time_us"])
            for item in observations
        ]

        targets = sorted({
            item["target"]
            for item in observations
        })

        aggregated.append({
            "module": module_name,
            "target_count": len(targets),
            "occurrence_count": len(observations),
            "median_self_time_us": statistics.median(self_times),
            "maximum_self_time_us": max(self_times),
            "median_cumulative_time_us": statistics.median(
                cumulative_times
            ),
            "targets": targets,
        })

    return sorted(
        aggregated,
        key=lambda item: (
            item["median_self_time_us"],
            item["target_count"],
        ),
        reverse=True,
    )


def get_distribution_versions(
    package_name: str,
) -> dict[str, str]:
    top_level = package_name.split(".", 1)[0]

    try:
        distributions = (
            importlib.metadata.packages_distributions()
            .get(top_level, [])
        )

    except (OSError, ValueError):
        return {}

    versions: dict[str, str] = {}

    for distribution in distributions:
        try:
            versions[distribution] = (
                importlib.metadata.version(distribution)
            )

        except importlib.metadata.PackageNotFoundError:
            continue

    return versions


def format_memory(value: float | None) -> str:
    if value is None:
        return "-"

    if abs(value) < 1024:
        return f"{value:.0f} B"

    if abs(value) < 1024**2:
        return f"{value / 1024:.1f} KB"

    return f"{value / 1024**2:.2f} MB"


def format_time(value: float | None) -> str:
    if value is None:
        return "-"

    if abs(value) < 1:
        return f"{value * 1000:.0f} µs"

    return f"{value:.2f} ms"


def median_of(
    result: dict[str, Any],
    key: str,
) -> float | None:
    return result[key]["median"]


def print_discovery(result: dict[str, Any]) -> None:
    print("\nPACKAGE DISCOVERY")
    print(
        f"  {result['module_count']} modules"
        f" | {format_time(median_of(result, 'runtime_ms'))}"
        f" | retained "
        f"{format_memory(median_of(result, 'retained_allocation_delta_bytes'))}"
        f" | peak "
        f"{format_memory(median_of(result, 'peak_allocation_delta_bytes'))}"
        f" | n={result['repetitions']}"
    )


def print_import_table(
    title: str,
    results: list[dict[str, Any]],
) -> None:
    if not results:
        return

    print(f"\n{title}")
    print(
        f"{'MODULE':<50}"
        f"{'TIME':>10}"
        f"{'RETAINED':>12}"
        f"{'PEAK':>12}"
        f"{'RSS Δ':>12}"
        f"{'LOADED':>10}"
    )
    print("-" * 106)

    for result in results:
        target = result["target"]

        if len(target) > 47:
            target = "..." + target[-44:]

        runtime = median_of(result, "runtime_ms")
        retained = median_of(
            result,
            "retained_allocation_delta_bytes",
        )
        peak = median_of(
            result,
            "peak_allocation_delta_bytes",
        )
        rss = median_of(result, "rss_delta_bytes")

        loaded = result["already_loaded"]
        loaded_label = (
            f"{loaded['count']}/{loaded['total']}"
        )

        errors = len(result["errors"])

        if errors:
            loaded_label += f" E{errors}"

        print(
            f"{target:<50}"
            f"{format_time(runtime):>10}"
            f"{format_memory(retained):>12}"
            f"{format_memory(peak):>12}"
            f"{format_memory(rss):>12}"
            f"{loaded_label:>10}"
        )

    print(
        "\n  Median values | RSS delta is paired per-run | "
        f"n={results[0]['requested_repetitions']}"
    )
    print(
        "  LOADED = already present in sys.modules / successful runtime runs"
    )


def print_import_profiles(
    profiles: list[dict[str, Any]],
    aggregates: list[dict[str, Any]],
    limit: int,
) -> None:
    successful = [
        profile
        for profile in profiles
        if profile["error"] is None
    ]

    failed = len(profiles) - len(successful)

    total_loads = sum(
        len(profile["newly_loaded_modules"])
        for profile in successful
    )

    unique_loads = {
        module
        for profile in successful
        for module in profile["newly_loaded_modules"]
    }

    print("\nIMPORT PROFILE")
    print(
        f"  {len(successful)} successful targets"
        f" | {total_loads} module loads across profiles"
        f" | {len(unique_loads)} unique modules"
        f" | {failed} failed profiles"
    )

    if not aggregates:
        print("  No import-time entries available.")
        return

    selected = aggregates[:limit]

    print(
        f"\n  Top {len(selected)} dependencies by median self-time"
    )
    print(
        f"  {'DEPENDENCY':<38}"
        f"{'TARGETS':>9}"
        f"{'MEDIAN SELF':>14}"
        f"{'MAX SELF':>12}"
    )

    for item in selected:
        module = item["module"]

        if len(module) > 35:
            module = "..." + module[-32:]

        print(
            f"  {module:<38}"
            f"{item['target_count']:>9}"
            f"{item['median_self_time_us'] / 1000:>11.2f} ms"
            f"{item['maximum_self_time_us'] / 1000:>9.2f} ms"
        )

    cumulative = sorted(
        aggregates,
        key=lambda item: item["median_cumulative_time_us"],
        reverse=True,
    )[:limit]

    print(
        f"\n  Top {len(cumulative)} dependencies by median cumulative time"
    )
    print(
        f"  {'DEPENDENCY':<38}"
        f"{'TARGETS':>9}"
        f"{'MEDIAN CUMULATIVE':>20}"
    )

    for item in cumulative:
        module = item["module"]

        if len(module) > 35:
            module = "..." + module[-32:]

        print(
            f"  {module:<38}"
            f"{item['target_count']:>9}"
            f"{item['median_cumulative_time_us'] / 1000:>17.2f} ms"
        )

def build_report(
    package_name: str,
    arguments: argparse.Namespace,
    environment: dict[str, str],
) -> dict[str, Any]:
    started = time.perf_counter()

    print(f"\n{'=' * 100}")
    print(f"PACKAGE: {package_name}")
    print(f"{'=' * 100}")

    modules, module_details, discovery = discover_modules(
        package_name,
        arguments.repetitions,
        environment,
        arguments.timeout,
    )

    print_discovery(discovery)

    package_results = measure_imports(
        [package_name],
        arguments.repetitions,
        package_name,
        environment,
        arguments.timeout,
        incremental=False,
        seed=arguments.seed,
    )

    package_result = package_results[0]

    print_import_table(
        "PACKAGE IMPORT",
        [package_result],
    )

    cold_results = measure_imports(
        modules,
        arguments.repetitions,
        package_name,
        environment,
        arguments.timeout,
        incremental=False,
        seed=arguments.seed,
    )

    print_import_table(
        "COLD MODULE IMPORTS",
        cold_results,
    )

    incremental_results: list[dict[str, Any]] = []

    if not arguments.no_incremental:
        incremental_results = measure_imports(
            modules,
            arguments.repetitions,
            package_name,
            environment,
            arguments.timeout,
            incremental=True,
            seed=arguments.seed + 1,
        )

        print_import_table(
            "PACKAGE-INITIALIZED MODULE IMPORTS",
            incremental_results,
        )

    profiles: list[dict[str, Any]] = []

    if arguments.import_profiles:
        generator = random.Random(arguments.seed + 2)
        profile_targets = list(modules)
        generator.shuffle(profile_targets)

        profiles = [
            profile_imports(
                module,
                package_name,
                environment,
                arguments.timeout,
            )
            for module in profile_targets
        ]

    aggregates = aggregate_import_profiles(profiles)

    if arguments.import_profiles:
        print_import_profiles(
            profiles,
            aggregates,
            arguments.profile_limit,
        )

    elapsed = time.perf_counter() - started

    return {
        "package": package_name,
        "package_versions": get_distribution_versions(package_name),
        "elapsed_seconds": elapsed,
        "discovery": discovery,
        "modules": modules,
        "module_details": module_details,
        "package_import": package_result,
        "cold_imports": cold_results,
        "package_initialized_imports": incremental_results,
        "import_profiles": {
            "enabled": arguments.import_profiles,
            "profiles": profiles,
            "aggregated_dependencies": aggregates,
        },
    }

def print_package_summary(
    reports: list[dict[str, Any]],
) -> None:
    print(f"\n{'=' * 100}")
    print("PACKAGE COMPARISON")
    print(f"{'=' * 100}")

    print(
        f"{'PACKAGE':<38}"
        f"{'MODULES':>10}"
        f"{'IMPORT':>12}"
        f"{'RETAINED':>12}"
        f"{'PEAK':>12}"
        f"{'DURATION':>12}"
    )

    print("-" * 96)

    for report in reports:
        package_name = report["package"]

        if len(package_name) > 35:
            package_name = "..." + package_name[-32:]

        discovery = report["discovery"]
        package_import = report["package_import"]

        print(
            f"{package_name:<38}"
            f"{discovery['module_count']:>10}"
            f"{format_time(median_of(package_import, 'runtime_ms')):>12}"
            f"{format_memory(median_of(package_import, 'retained_allocation_delta_bytes')):>12}"
            f"{format_memory(median_of(package_import, 'peak_allocation_delta_bytes')):>12}"
            f"{report['elapsed_seconds']:>11.2f} s"
        )
def main() -> int:
    arguments = parse_arguments()

    if arguments.repetitions < 1:
        print("Error: repetitions must be at least 1.")
        return 2

    if arguments.profile_limit < 1:
        print("Error: profile limit must be at least 1.")
        return 2

    if arguments.timeout <= 0:
        print("Error: timeout must be greater than zero.")
        return 2

    print("Python package import benchmark")
    print(
        f"Python {platform.python_version()}"
        f" | {platform.system()} {platform.machine()}"
        f" | preset={arguments.preset}"
        f" | repetitions={arguments.repetitions}"
        f" | packages={len(arguments.package_paths)}"
    )

    try:
        environment, python_paths = build_worker_environment(
            arguments
        )

        started = time.perf_counter()

        reports: list[dict[str, Any]] = []
        package_errors: list[dict[str, str]] = []

        for package_name in arguments.package_paths:
            try:
                report = build_report(
                    package_name,
                    arguments,
                    environment,
                )

                reports.append(report)

            except (
                OSError,
                RuntimeError,
                ValueError,
                TypeError,
                SyntaxError,
            ) as error:
                package_errors.append({
                    "package": package_name,
                    "message": str(error),
                })

                print(
                    f"\nPACKAGE FAILED: {package_name}\n"
                    f"  {error}"
                )

        elapsed = time.perf_counter() - started

        if reports:
            print_package_summary(reports)

        consolidated_report = {
            "schema_version": REPORT_SCHEMA_VERSION,
            "metadata": {
                "packages": arguments.package_paths,
                "python_version": sys.version,
                "python_implementation": platform.python_implementation(),
                "platform": platform.platform(),
                "executable": sys.executable,
                "working_directory": str(Path.cwd()),
                "python_path": python_paths,
                "parent_sys_path": sys.path,
                "timestamp": datetime.datetime.now().astimezone().isoformat(),
                "preset": arguments.preset,
                "repetitions": arguments.repetitions,
                "timeout_seconds": arguments.timeout,
                "random_seed": arguments.seed,
                "module_order": (
                    "deterministic randomized per repetition"
                ),
                "elapsed_seconds": elapsed,
            },
            "packages": reports,
            "errors": package_errors,
        }

        output_path = arguments.json_output.expanduser().resolve()

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path.write_text(
            json.dumps(
                consolidated_report,
                indent=2,
                ensure_ascii=False,
            ) + "\n",
            encoding="utf-8",
        )

        print("\nBENCHMARK COMPLETE")
        print(f"  Successful packages: {len(reports)}")
        print(f"  Failed packages: {len(package_errors)}")
        print(f"  Duration: {elapsed:.2f} s")
        print(f"  JSON: {output_path}")

        module_errors = sum(
            len(result["errors"])
            for report in reports
            for result in (
                report["cold_imports"]
                + report["package_initialized_imports"]
                + [report["package_import"]]
            )
        )

        profile_errors = sum(
            profile["error"] is not None
            for report in reports
            for profile in report["import_profiles"]["profiles"]
        )

        if module_errors or profile_errors:
            print(
                f"  Warnings: {module_errors} measurement errors, "
                f"{profile_errors} profile errors"
            )

        return 1 if package_errors else 0

    except (
        OSError,
        RuntimeError,
        ValueError,
        TypeError,
        SyntaxError,
    ) as error:
        print(f"\nBenchmark failed: {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

