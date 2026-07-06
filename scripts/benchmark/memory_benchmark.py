#!/usr/bin/env python3
"""
Benchmark memory usage for RustPython vs CPython
"""
import subprocess
import json
import re
from pathlib import Path

def get_memory_usage(executable, code):
    """Run code and measure memory usage using /usr/bin/time"""
    import tempfile
    import os
    
    # Write code to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        # Use /usr/bin/time -v to get memory info
        result = subprocess.run(
            ["/usr/bin/time", "-v", executable, temp_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Parse memory from stderr
        stderr = result.stderr
        memory_info = {}
        
        # Extract max resident set size
        match = re.search(r'Maximum resident set size \(kbytes\): (\d+)', stderr)
        if match:
            memory_info["max_rss_kb"] = int(match.group(1))
        
        # Extract heap size if available
        match = re.search(r'Maximum heap size \(kbytes\): (\d+)', stderr)
        if match:
            memory_info["heap_kb"] = int(match.group(1))
        
        return memory_info, result.stdout
    except Exception as e:
        return {"error": str(e)}, ""
    finally:
        os.unlink(temp_file)

def main():
    project_root = Path(__file__).parent.parent.parent
    rustpython = project_root / "builds" / "rustpython" / "target" / "release" / "rustpython"
    cpython = project_root / "builds" / "cpython" / "python"
    
    test_code = {
        "empty": "pass",
        "small_list": "x = list(range(10000))",
        "small_dict": "x = {i: i*2 for i in range(10000)}",
        "string_concat": "x = ''.join(str(i) for i in range(10000))",
        "recursion": """
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)
fib(20)
"""
    }
    
    results = {
        "rustpython": {},
        "cpython": {},
        "timestamp": subprocess.check_output(["date"]).decode().strip()
    }
    
    print("=== Memory Usage Benchmark ===\n")
    
    for test_name, code in test_code.items():
        print(f"Running {test_name}...")
        
        # Test RustPython
        rp_mem, rp_output = get_memory_usage(str(rustpython), code)
        results["rustpython"][test_name] = {
            "memory": rp_mem,
            "output": rp_output[:100] if rp_output else ""
        }
        
        # Test CPython
        cp_mem, cp_output = get_memory_usage(str(cpython), code)
        results["cpython"][test_name] = {
            "memory": cp_mem,
            "output": cp_output[:100] if cp_output else ""
        }
        
        if "max_rss_kb" in rp_mem and "max_rss_kb" in cp_mem:
            print(f"  CPython: {cp_mem['max_rss_kb']} KB, RustPython: {rp_mem['max_rss_kb']} KB")
    
    # Save results
    output_file = project_root / "results" / "raw-data" / "memory-usage.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
