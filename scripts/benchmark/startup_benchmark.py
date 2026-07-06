#!/usr/bin/env python3
"""
Benchmark startup time for RustPython vs CPython
"""
import subprocess
import time
import json
import statistics
from pathlib import Path

def measure_startup(executable, iterations=10):
    """Measure startup time of a Python executable"""
    times = []
    
    for _ in range(iterations):
        start = time.perf_counter()
        result = subprocess.run(
            [executable, "-c", "pass"],
            capture_output=True,
            timeout=10
        )
        end = time.perf_counter()
        
        if result.returncode == 0:
            times.append((end - start) * 1000)  # Convert to milliseconds
    
    if times:
        return {
            "mean_ms": statistics.mean(times),
            "median_ms": statistics.median(times),
            "stdev_ms": statistics.stdev(times) if len(times) > 1 else 0,
            "min_ms": min(times),
            "max_ms": max(times),
            "iterations": len(times)
        }
    return None

def main():
    project_root = Path(__file__).parent.parent.parent
    rustpython = project_root / "builds" / "rustpython" / "target" / "release" / "rustpython"
    cpython = project_root / "builds" / "cpython" / "python"
    
    results = {
        "rustpython": measure_startup(str(rustpython)),
        "cpython": measure_startup(str(cpython)),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Save results
    output_file = project_root / "results" / "raw-data" / "startup-times.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("=== Startup Time Benchmark ===")
    print(f"{'Implementation':<15} {'Mean (ms)':<15} {'Median (ms)':<15} {'Min (ms)':<15}")
    print("-" * 60)
    
    for impl, data in results.items():
        if impl == "timestamp":
            continue
        if data:
            print(f"{impl:<15} {data['mean_ms']:<15.2f} {data['median_ms']:<15.2f} {data['min_ms']:<15.2f}")
    
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
