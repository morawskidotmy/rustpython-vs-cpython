# Test Methodology

This document describes the methodology used for benchmarking and comparing RustPython and CPython.

## Table of Contents

1. [Overview](#overview)
2. [Benchmark Categories](#benchmark-categories)
3. [Measurement Techniques](#measurement-techniques)
4. [Statistical Analysis](#statistical-analysis)
5. [Test Environment](#test-environment)
6. [Reproducibility](#reproducibility)

---

## Overview

The comparison focuses on three main dimensions:

1. **Performance**: How fast does the implementation execute code?
2. **Memory Usage**: How much memory does the implementation consume?
3. **Compatibility**: How well does the implementation support Python syntax and standard library?

Each dimension is measured using multiple benchmarks to ensure comprehensive coverage.

---

## Benchmark Categories

### 1. Startup Time

**Purpose**: Measure the time from invoking the interpreter to being ready to execute code.

**Method**:
- Run `python -c "pass"` multiple times
- Measure wall-clock time using `time.perf_counter()`
- Calculate mean, median, standard deviation

**Limitations**:
- Process launch overhead included (not just interpreter init)
- No warmup runs (first run may be slower)
- Only 10 iterations (statistical significance is limited)

**Why It Matters**:
- Affects interactive use (REPL)
- Impacts short-running scripts
- Important for command-line tools

**Test Script**: [`scripts/benchmark/startup_benchmark.py`](scripts/benchmark/startup_benchmark.py)

---

### 2. Execution Speed

**Purpose**: Measure how fast the implementation executes Python code.

**Subcategories**:

#### 2.1 Arithmetic Operations
- Integer addition, subtraction, multiplication
- Floating-point operations
- Exponentiation

#### 2.2 String Operations
- Concatenation
- Formatting (f-strings)
- Regular expressions

#### 2.3 Data Structure Operations
- List creation, indexing, slicing
- Dictionary insertion, lookup
- Set operations

#### 2.4 Function Calls
- Simple function calls
- Recursive functions
- Arguments passing

#### 2.5 Loop Performance
- For loops
- While loops
- Comprehensions

**Method**:
- Execute each benchmark 5-10 times
- Measure execution time using `time.perf_counter()`
- Calculate statistics

**Test Script**: [`scripts/benchmark/execution_benchmark.py`](scripts/benchmark/execution_benchmark.py)

---

### 3. Memory Usage

**Purpose**: Measure memory consumption during code execution.

**Method**:
- Use `/usr/bin/time -v` to measure maximum resident set size
- Run various test cases (empty, small data structures, recursion)
- Record peak memory usage

**Metrics**:
- Maximum resident set size (RSS) in KB
- Heap size (if available)

**Why It Matters**:
- Important for memory-constrained environments
- Affects scalability
- Indicates memory efficiency

**Test Script**: [`scripts/benchmark/memory_benchmark.py`](scripts/benchmark/memory_benchmark.py)

---

### 4. Compatibility

**Purpose**: Determine how well each implementation supports Python syntax and standard library.

**Subcategories**:

#### 4.1 Syntax Support
Tests whether the implementation supports Python 3.14 syntax features:
- F-strings
- Type hints
- Pattern matching (`match`/`case`)
- Walrus operator (`:=`)
- Async/await
- Decorators
- Context managers
- Generators
- Comprehensions (list, set, dict)

#### 4.2 Standard Library Coverage
Tests whether standard library modules can be imported:
- `os`, `sys`, `json`, `math`, `random`
- `collections`, `itertools`, `functools`
- `pathlib`, `subprocess`, `re`
- `hashlib`, `base64`, `csv`
- `sqlite3`, `unittest`
- `typing`, `dataclasses`, `enum`

**Method**:
- Attempt to import each module
- Record success/failure
- Capture error messages

**Test Script**: [`scripts/benchmark/compatibility_test.py`](scripts/benchmark/compatibility_test.py)

---

## Measurement Techniques

### Time Measurement

**Tools**:
- Python's `time.perf_counter()`: High-resolution timer
- Unix `time` command: For memory measurement
- Bash `time` builtin: For simple measurements

**Best Practices**:
- Warm-up runs (discard first measurement)
- Multiple iterations (5-10 minimum)
- Statistical analysis (mean, median, stdev)

**Code Example**:
```python
import time

start = time.perf_counter()
# Code to benchmark
end = time.perf_counter()
elapsed = end - start
```

---

### Memory Measurement

**Tools**:
- `/usr/bin/time -v`: Provides detailed memory statistics
- `tracemalloc` (Python module): For in-Python memory tracking
- `psutil` (Python module): For process memory information

**Metrics**:
- Maximum resident set size (RSS)
- Heap size
- Virtual memory size

**Code Example**:
```python
import tracemalloc

tracemalloc.start()
# Code to benchmark
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()
```

---

## Statistical Analysis

### Metrics Calculated

For each benchmark:
- **Mean**: Average value
- **Median**: Middle value (robust to outliers)
- **Standard Deviation**: Measure of variability
- **Min/Max**: Range of values
- **Iterations**: Number of successful runs

### Outlier Detection

- Discard runs with errors
- Visual inspection of results
- Standard deviation thresholding

### Confidence

- Minimum 5 iterations per benchmark
- More iterations for variable results
- Report standard deviation to indicate variability

---

## Test Environment

### Hardware
- **CPU**: Multi-core processor (e.g., Intel i5/i7 or AMD equivalent)
- **RAM**: 8GB+ recommended
- **Disk**: SSD recommended for faster builds

### Software
- **OS**: Linux (Ubuntu/Debian recommended)
- **Compiler**: GCC or Clang (for CPython)
- **Rust**: Latest stable (1.95.0+)
- **Python**: 3.8+ (for running benchmark scripts)

### Environment Variables

For consistent results:
```bash
# Disable CPU frequency scaling
echo "performance" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Disable ASLR (optional, for more consistent results)
echo 0 | sudo tee /proc/sys/kernel/randomize_va_space
```

---

## Reproducibility

### Ensuring Reproducible Results

1. **Version Control**: Use specific git tags/commits
2. **Clean Builds**: Rebuild from scratch for critical measurements
3. **Documentation**: Record all commands and configurations
4. **Scripts**: Automate benchmarks to avoid human error

### Running Reproducible Benchmarks

```bash
# 1. Clone and build (see build-instructions.md)

# 2. Run all benchmarks
cd /path/to/rustvscpython
python3 scripts/benchmark/startup_benchmark.py
python3 scripts/benchmark/execution_benchmark.py
python3 scripts/benchmark/memory_benchmark.py
python3 scripts/benchmark/compatibility_test.py

# 3. Generate visualizations
python3 scripts/visualize/generate_charts.py

# 4. View results
ls -la results/
```

### Comparing Different Versions

To compare different versions of CPython or RustPython:

1. Checkout the desired version
2. Rebuild
3. Rerun benchmarks
4. Compare results

---

## Limitations

### What This Methodology Doesn't Cover

1. **Real-world Applications**: Benchmarks are synthetic, not real applications
2. **Long-running Processes**: Memory leaks over time not tested
3. **Concurrency**: Multi-threaded performance not benchmarked
4. **C Extensions**: Compatibility with C extension modules not fully tested
5. **I/O Performance**: Disk/network I/O not benchmarked

### Sources of Error

1. **System Load**: Other processes affect results
2. **CPU Frequency Scaling**: Dynamic frequency affects performance
3. **Cache Effects**: First run may be slower due to cold cache
4. **Measurement Overhead**: `time.perf_counter()` has small overhead

### Mitigation Strategies

1. Run benchmarks on idle system
2. Disable CPU frequency scaling
3. Multiple warm-up runs
4. Statistical analysis to identify outliers

---

## Future Improvements

Planned improvements to the methodology:

1. **More Benchmarks**: Add real-world application benchmarks
2. **Profiling**: Add CPU and memory profiling
3. **CI/CD**: Automated benchmarking on multiple platforms
4. **Interactive Dashboard**: Web-based visualization
5. **Historical Tracking**: Track performance over time

---

## References

- Python Benchmarks: https://devguide.python.org/performance/
- Rust Performance Book: https://rust-lang.github.io/packed_simd/perf-guide/
- Statistical Analysis: https://en.wikipedia.org/wiki/Statistical_significance
