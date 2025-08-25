#!/usr/bin/env python
"""Script to determine the optimal number of test workers."""

import multiprocessing
import subprocess
import sys
import time


def run_tests_with_workers(num_workers: int, test_path: str = "tests") -> float:
    """Run tests with a specified number of workers and return execution time."""
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        test_path,
        "-q",
        "--tb=no",
        "--no-cov",
        "-n",
        str(num_workers),
    ]

    start = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    elapsed = time.time() - start

    if result.returncode != 0:
        print(f"Tests failed with {num_workers} workers")
        return float("inf")

    return elapsed


def main():
    """Find the optimal number of workers for test execution."""
    cpu_count = multiprocessing.cpu_count()
    test_path = sys.argv[1] if len(sys.argv) > 1 else "tests/scrapers"

    print(f"Testing with different worker counts (CPU cores: {cpu_count})")
    print(f"Test path: {test_path}\n")

    results = {}

    # Test with different worker counts
    worker_counts = [1, 2, 4, cpu_count, cpu_count * 2]
    worker_counts = [w for w in worker_counts if w <= 16]  # Cap at 16 workers
    worker_counts = sorted(set(worker_counts))

    for workers in worker_counts:
        print(f"Testing with {workers} worker(s)...", end=" ", flush=True)
        elapsed = run_tests_with_workers(workers, test_path)
        results[workers] = elapsed
        print(f"{elapsed:.2f}s")

    # Find optimal
    optimal = min(results, key=results.get)
    baseline = results.get(1, float("inf"))

    print("\nResults Summary:")
    print("-" * 40)
    for workers, elapsed in sorted(results.items()):
        speedup = baseline / elapsed if elapsed > 0 else 0
        print(f"{workers:2} workers: {elapsed:6.2f}s (speedup: {speedup:.2f}x)")

    print(f"\nOptimal configuration: {optimal} workers")
    print(f"Speedup vs serial: {baseline / results[optimal]:.2f}x")

    # Update pyproject.toml recommendation
    print("\nRecommendation for pyproject.toml:")
    print(f'  "-n={optimal}",  # Optimal for this system')


if __name__ == "__main__":
    main()
