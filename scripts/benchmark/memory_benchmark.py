#!/usr/bin/env python3
"""
Benchmark memory usage for RustPython vs CPython using psutil
"""
import subprocess
import json
import tempfile
import os
import time
import psutil
from pathlib import Path

TEST_CASES = {
    "empty": "pass",
    "small_list": "x = list(range(10000))",
    "small_dict": "x = {i: i*2 for i in range(10000)}",
    "string_concat": "x = ''.join(str(i) for i in range(10000))",
    "large_list": "x = [i**2 for i in range(100000)]; y = [i*3 for i in x]",
    "nested_dict": "x = {i: {j: j*i for j in range(100)} for i in range(1000)}",
    "recursion": """
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)
fib(20)
""",
    "class_objects": """
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
points = [Point(i, i*2) for i in range(10000)]
"""
}

def measure_memory(executable, code, iterations=3):
    """Run code multiple times and measure peak RSS memory"""
    peak_memories = []
    
    for _ in range(iterations):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            process = subprocess.Popen(
                [executable, temp_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Monitor memory usage
            max_rss = 0
            try:
                ps_process = psutil.Process(process.pid)
                # Get children too (some implementations spawn workers)
                all_procs = [ps_process] + ps_process.children(recursive=True)
                
                for proc in all_procs:
                    try:
                        mem = proc.memory_info()
                        max_rss = max(max_rss, mem.rss)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                # Poll while running
                while process.poll() is None:
                    try:
                        for proc in all_procs:
                            mem = proc.memory_info()
                            max_rss = max(max_rss, mem.rss)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                    time.sleep(0.01)  # 10ms polling
                
            except psutil.NoSuchProcess:
                pass
            
            process.wait(timeout=30)
            
            if process.returncode == 0:
                peak_memories.append(max_rss)
        
        except Exception as e:
            pass
        finally:
            os.unlink(temp_file)
    
    if peak_memories:
        return {
            "peak_rss_bytes": max(peak_memories),
            "peak_rss_mb": max(peak_memories) / (1024 * 1024),
            "avg_rss_bytes": sum(peak_memories) / len(peak_memories),
            "avg_rss_mb": (sum(peak_memories) / len(peak_memories)) / (1024 * 1024),
            "iterations": len(peak_memories),
            "success": True
        }
    
    return {"success": False, "error": "All iterations failed"}

def main():
    project_root = Path(__file__).parent.parent.parent
    rustpython = project_root / "builds" / "rustpython" / "target" / "release" / "rustpython"
    cpython = project_root / "builds" / "cpython" / "python"
    
    results = {
        "rustpython": {},
        "cpython": {},
        "timestamp": subprocess.check_output(["date"]).decode().strip()
    }
    
    print("=== Memory Usage Benchmark (psutil RSS) ===\n")
    
    for test_name, code in TEST_CASES.items():
        print(f"Running {test_name}...")
        
        # Test CPython
        cp_mem = measure_memory(str(cpython), code)
        results["cpython"][test_name] = cp_mem
        
        # Test RustPython
        rp_mem = measure_memory(str(rustpython), code)
        results["rustpython"][test_name] = rp_mem
        
        if cp_mem.get("success") and rp_mem.get("success"):
            ratio = rp_mem["peak_rss_mb"] / cp_mem["peak_rss_mb"] if cp_mem["peak_rss_mb"] > 0 else 0
            print(f"  CPython: {cp_mem['peak_rss_mb']:.2f} MB, RustPython: {rp_mem['peak_rss_mb']:.2f} MB (ratio: {ratio:.2f}x)")
        elif cp_mem.get("success"):
            print(f"  CPython: {cp_mem['peak_rss_mb']:.2f} MB, RustPython: failed")
        elif rp_mem.get("success"):
            print(f"  CPython: failed, RustPython: {rp_mem['peak_rss_mb']:.2f} MB")
        else:
            print(f"  Both failed")
    
    # Save results
    output_file = project_root / "results" / "raw-data" / "memory-usage.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
