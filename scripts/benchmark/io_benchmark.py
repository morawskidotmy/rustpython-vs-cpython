#!/usr/bin/env python3
"""
Benchmark I/O operations for RustPython vs CPython
"""
import subprocess
import json
import tempfile
import os
import time
from pathlib import Path

IO_BENCHMARKS = {
    "file_write": """
import tempfile
import os
with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
    for i in range(10000):
        f.write(f"Line {i}: This is a test line with some content\\n")
    temp_path = f.name
os.unlink(temp_path)
""",
    "file_read": """
import tempfile
import os
with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
    for i in range(10000):
        f.write(f"Line {i}: This is a test line with some content\\n")
    temp_path = f.name
with open(temp_path, 'r') as f:
    lines = f.readlines()
os.unlink(temp_path)
""",
    "file_read_write": """
import tempfile
import os
with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as f:
    for i in range(5000):
        f.write(f"Line {i}\\n")
    f.seek(0)
    lines = f.readlines()
    for line in lines[:100]:
        f.write(line.upper())
os.unlink(f.name)
""",
    "json_file": """
import json
import tempfile
import os
data = {f"key_{i}": [i, i*2, i*3] for i in range(1000)}
with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
    json.dump(data, f)
    temp_path = f.name
with open(temp_path, 'r') as f:
    loaded = json.load(f)
os.unlink(temp_path)
""",
    "csv_file": """
import csv
import tempfile
import os
with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
    writer = csv.writer(f)
    writer.writerow(['Name', 'Age', 'City'])
    for i in range(5000):
        writer.writerow([f'Person{i}', 20 + (i % 50), f'City{i % 10}'])
    temp_path = f.name
with open(temp_path, 'r') as f:
    reader = csv.reader(f)
    rows = list(reader)
os.unlink(temp_path)
"""
}

def run_benchmark(executable, code, iterations=5):
    """Run a benchmark multiple times and return statistics"""
    times = []
    
    for _ in range(iterations):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            start = time.perf_counter()
            result = subprocess.run(
                [executable, temp_file],
                capture_output=True,
                text=True,
                timeout=60
            )
            end = time.perf_counter()
            
            if result.returncode == 0:
                times.append(end - start)
        except Exception:
            pass
        finally:
            os.unlink(temp_file)
    
    if times:
        return {
            "mean": sum(times) / len(times),
            "min": min(times),
            "max": max(times),
            "iterations": len(times),
            "success": True
        }
    return {"success": False}

def main():
    project_root = Path(__file__).parent.parent.parent
    rustpython = project_root / "builds" / "rustpython" / "target" / "release" / "rustpython"
    cpython = project_root / "builds" / "cpython" / "python"
    
    results = {
        "rustpython": {},
        "cpython": {},
        "timestamp": subprocess.check_output(["date"]).decode().strip()
    }
    
    print("=== I/O Operations Benchmark ===\n")
    
    for benchmark_name, code in IO_BENCHMARKS.items():
        print(f"Running {benchmark_name}...")
        
        cp_result = run_benchmark(str(cpython), code)
        rp_result = run_benchmark(str(rustpython), code)
        
        results["cpython"][benchmark_name] = cp_result
        results["rustpython"][benchmark_name] = rp_result
        
        if cp_result.get("success") and rp_result.get("success"):
            ratio = rp_result["mean"] / cp_result["mean"] if cp_result["mean"] > 0 else 0
            print(f"  CPython: {cp_result['mean']:.3f}s, RustPython: {rp_result['mean']:.3f}s (ratio: {ratio:.2f}x)")
        elif cp_result.get("success"):
            print(f"  CPython: {cp_result['mean']:.3f}s, RustPython: failed")
        elif rp_result.get("success"):
            print(f"  CPython: failed, RustPython: {rp_result['mean']:.3f}s")
        else:
            print(f"  Both failed")
    
    # Save results
    output_file = project_root / "results" / "raw-data" / "io-benchmarks.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
