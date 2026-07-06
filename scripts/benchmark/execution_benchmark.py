#!/usr/bin/env python3
"""
Benchmark execution speed for various Python operations
"""
import subprocess
import time
import json
import statistics
from pathlib import Path

BENCHMARKS = {
    "arithmetic": """
# Arithmetic operations benchmark
import time
start = time.perf_counter()
result = 0
for i in range(1000000):
    result += i * 2 - i // 2 + i ** 2
end = time.perf_counter()
print(f"{end - start:.6f}")
""",
    "string_ops": """
# String operations benchmark
import time
start = time.perf_counter()
result = ""
for i in range(10000):
    result += f"Number: {i}, "
    result = result.replace(" ", "-")
end = time.perf_counter()
print(f"{end - start:.6f}")
""",
    "list_ops": """
# List operations benchmark
import time
start = time.perf_counter()
data = list(range(10000))
result = [x * 2 for x in data if x % 2 == 0]
result.sort(reverse=True)
end = time.perf_counter()
print(f"{end - start:.6f}")
""",
    "dict_ops": """
# Dictionary operations benchmark
import time
start = time.perf_counter()
data = {i: i * 2 for i in range(10000)}
result = {k: v for k, v in data.items() if k % 3 == 0}
end = time.perf_counter()
print(f"{end - start:.6f}")
""",
    "loop_performance": """
# Loop performance benchmark
import time
start = time.perf_counter()
result = 0
for i in range(1000000):
    result += i
end = time.perf_counter()
print(f"{end - start:.6f}")
""",
    "function_calls": """
# Function call overhead benchmark
import time
def add(a, b):
    return a + b
start = time.perf_counter()
result = 0
for i in range(1000000):
    result = add(result, i)
end = time.perf_counter()
print(f"{end - start:.6f}")
"""
}

def run_benchmark(executable, code, iterations=5):
    """Run a benchmark multiple times and return statistics"""
    times = []
    
    for _ in range(iterations):
        result = subprocess.run(
            [executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            try:
                elapsed = float(result.stdout.strip())
                times.append(elapsed)
            except ValueError:
                pass
    
    if times:
        return {
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "stdev": statistics.stdev(times) if len(times) > 1 else 0,
            "min": min(times),
            "max": max(times),
            "iterations": len(times)
        }
    return None

def main():
    project_root = Path(__file__).parent.parent.parent
    rustpython = project_root / "builds" / "rustpython" / "target" / "release" / "rustpython"
    cpython = project_root / "builds" / "cpython" / "python"
    
    results = {
        "rustpython": {},
        "cpython": {},
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    print("=== Execution Speed Benchmark ===\n")
    
    for benchmark_name, code in BENCHMARKS.items():
        print(f"Running {benchmark_name}...")
        
        rp_result = run_benchmark(str(rustpython), code)
        cp_result = run_benchmark(str(cpython), code)
        
        results["rustpython"][benchmark_name] = rp_result
        results["cpython"][benchmark_name] = cp_result
        
        if rp_result and cp_result:
            ratio = rp_result["mean"] / cp_result["mean"] if cp_result["mean"] > 0 else 0
            print(f"  CPython: {cp_result['mean']:.4f}s, RustPython: {rp_result['mean']:.4f}s (ratio: {ratio:.2f}x)")
    
    # Save results
    output_file = project_root / "results" / "raw-data" / "execution-speed.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
