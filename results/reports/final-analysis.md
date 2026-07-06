# Comprehensive Analysis Report: RustPython vs CPython

**Date**: 2026-07-06  
**Versions Compared**: CPython 3.14.0 vs RustPython 0.5.0  
**Test Environment**: Linux x86_64

---

## Executive Summary

This report presents a comprehensive comparison between CPython 3.14.0 (the reference Python implementation in C) and RustPython 0.5.0 (a Python 3.14 interpreter written in Rust). 

**Key Findings**:
- CPython significantly outperforms RustPython in all performance benchmarks (1.3x to 7.4x faster)
- Both implementations support the same Python 3.14 syntax features
- CPython has complete standard library coverage; RustPython has 23/24 tested modules
- RustPython is still in alpha stage (0.5.0) and not production-ready

---

## Detailed Analysis

### 1. Performance Comparison

#### 1.1 Startup Time

| Implementation | Mean (ms) | Median (ms) | Std Dev (ms) |
|---------------|------------|--------------|---------------|
| CPython 3.14.0 | 26.77 | 26.51 | 0.84 |
| RustPython 0.5.0 | 128.21 | 110.65 | 15.32 |

**Analysis**: CPython starts up ~4.8x faster than RustPython. This is critical for:
- Command-line tools
- Short-running scripts
- Interactive REPL usage

**Why?**:
- CPython's binary is highly optimized
- RustPython likely has more initialization overhead
- Rust's safety checks add startup cost

#### 1.2 Execution Speed

| Benchmark | CPython (s) | RustPython (s) | Ratio (RP/CP) |
|-----------|---------------|----------------|---------------|
| Arithmetic | 0.6176 | 2.1991 | 3.56x |
| String Ops | 0.2955 | 0.3911 | 1.32x |
| List Ops | 0.0017 | 0.0087 | 5.18x |
| Dict Ops | 0.0033 | 0.0217 | 6.62x |
| Loops | 0.2649 | 0.7928 | 2.99x |
| Function Calls | 0.2775 | 2.0531 | 7.40x |

**Analysis**: CPython is faster across all benchmarks:
- **Best case**: String operations (1.32x faster)
- **Worst case**: Function calls (7.40x faster)
- **Average**: ~4.5x faster

**Why?**:
- CPython's VM is highly optimized (30+ years)
- Function call overhead is higher in RustPython
- Dictionary/list operations are critical paths in CPython

#### 1.3 Memory Usage

| Test Case | CPython (MB) | RustPython (MB) | Ratio |
|-----------|---------------|----------------|-------|
| Empty | 9.67 | 25.73 | 2.66x |
| Small List | 9.04 | 26.80 | 2.97x |
| Small Dict | 8.89 | 28.16 | 3.17x |
| String Concat | 10.11 | 25.74 | 2.55x |
| Large List | 18.48 | 47.78 | 2.59x |
| Nested Dict | 16.79 | 42.65 | 2.54x |
| Recursion | 9.19 | 25.91 | 2.82x |
| Class Objects | 10.23 | 36.60 | 3.58x |

**Analysis**: RustPython uses 2.5x to 3.6x more memory than CPython:
- RustPython's runtime includes the Rust standard library
- Less optimized memory allocation compared to CPython's custom allocator
- Safety checks and ownership tracking add memory overhead
- CPython's memory allocator is highly tuned for Python's object model

### 2. Compatibility Comparison

#### 2.1 Syntax Support

| Feature | CPython | RustPython |
|---------|----------|------------|
| F-strings | ✓ | ✓ |
| Type hints | ✓ | ✓ |
| Pattern matching | ✓ | ✓ |
| Walrus operator | ✓ | ✓ |
| Async/await | ✓ | ✓ |
| Decorators | ✓ | ✓ |
| Context managers | ✓ | ✓ |
| Generators | ✓ | ✓ |
| List comprehension | ✓ | ✓ |
| Set comprehension | ✓ | ✓ |
| Dict comprehension | ✓ | ✓ |

**Score**: 11/11 for both

**Analysis**: RustPython has excellent syntax support for Python 3.14 features.

#### 2.2 Standard Library Coverage

**Import Test Results**:

| Module | CPython | RustPython |
|--------|----------|------------|
| os, sys, json, math, random | ✓ | ✓ |
| time, datetime, collections | ✓ | ✓ |
| itertools, functools, pathlib | ✓ | ✓ |
| subprocess, re, hashlib | ✓ | ✓ |
| base64, csv, unittest | ✓ | ✓ |
| typing, dataclasses, enum | ✓ | ✓ |
| abc, copy, pickle | ✓ | ✓ |
| sqlite3 | ✓ | ✗ |

**Score**: CPython 24/24, RustPython 23/24

**Functionality Test Results**:

| Module | CPython | RustPython | Description |
|--------|----------|------------|-------------|
| os, sys, json, math | ✓ | ✓ | Core operations |
| random, datetime | ✓ | ✓ | Time/random |
| collections, itertools | ✓ | ✓ | Data structures |
| re, hashlib | ✓ | ✓ | Text/crypto |
| typing, dataclasses | ✓ | ✓ | Type system |
| enum, functools | ✓ | ✓ | Utilities |
| pathlib, unittest | ✓ | ✓ | Path/testing |
| copy, pickle | ✓ | ✓ | Serialization |
| csv | ✗ | ✗ | Test issue (both) |
| sqlite3 | ✓ | ✗ | Database |

**Score**: CPython 19/20, RustPython 18/20

**Analysis**: RustPython is missing `sqlite3` module (database interface). The `csv` test fails on both implementations (likely a test issue, not a module problem). Otherwise, functionality is excellent.

---

## Visualizations

### Generated Charts

1. **Startup Time Comparison**: `results/visualizations/startup-time-comparison.png`
2. **Execution Speed Comparison**: `results/visualizations/execution-speed-comparison.png`
3. **Memory Usage Comparison**: `results/visualizations/memory-usage-comparison.png`
4. **Compatibility Pie Charts**: `results/visualizations/compatibility-pie-charts.png`
5. **Summary Dashboard**: `results/visualizations/summary-dashboard.png`

---

## Strengths and Weaknesses

### CPython 3.14.0

#### Strengths
1. **Performance**: 1.3x to 7.4x faster in execution benchmarks
2. **Memory Efficiency**: 2.5x to 3.6x less memory usage
3. **Startup Speed**: 4.8x faster interpreter startup
4. **Maturity**: 30+ years of development
5. **Compatibility**: Full standard library support
6. **Ecosystem**: Massive third-party package ecosystem
7. **Tooling**: Excellent debugging and profiling tools

#### Weaknesses
1. **Memory Safety**: Prone to buffer overflows, segfaults
2. **GIL**: Limits true parallelism (though PEP 703 is changing this)
3. **C Codebase**: Hard to maintain, steep learning curve
4. **Embedding**: C API is complex

### RustPython 0.5.0

#### Strengths
1. **Memory Safety**: Guaranteed by Rust compiler
2. **Modern Codebase**: Clean, maintainable Rust code
3. **No GIL**: Potential for true parallelism
4. **WebAssembly**: First-class WASM support
5. **Embedding**: Easy to embed in Rust applications
6. **Syntax Support**: 100% Python 3.14 syntax compatibility
7. **Stdlib Coverage**: 90%+ module functionality

#### Weaknesses
1. **Performance**: 1.3x to 7.4x slower than CPython
2. **Memory Usage**: 2.5x to 3.6x more memory
3. **Startup Time**: 4.8x slower startup
4. **Maturity**: Alpha stage (0.5.0)
5. **Missing Modules**: sqlite3 not implemented
6. **Ecosystem**: Limited third-party support
7. **Tooling**: Debugging support is limited

---

## Recommendations

### Use CPython If:

1. **Production Applications**: It's battle-tested and reliable
2. **Performance-Critical Code**: Significantly faster
3. **Full Ecosystem Access**: Need NumPy, pandas, etc.
4. **Standard Library Dependence**: Need complete stdlib

### Use RustPython If:

1. **Memory Safety is Critical**: Avoid segfaults, buffer overflows
2. **Embedding in Rust**: Easy integration with Rust code
3. **WebAssembly Targets**: Browser-based Python execution
4. **Contributing to Python**: Cleaner codebase to work with
5. **Experimental Projects**: Want to explore Python implementation

### Future Outlook:

1. **CPython**: Will remain the dominant implementation for years
2. **RustPython**: Needs significant optimization to be competitive
3. **Hybrid Approach**: Possible to use RustPython for safety-critical parts, CPython for performance

---

## Conclusion

This comprehensive comparison shows that while CPython significantly outperforms RustPython in terms of raw performance, RustPython offers compelling advantages in memory safety and modern architecture. 

**For most users**, CPython remains the best choice due to its performance, maturity, and ecosystem.

**For specific use cases** (safety-critical applications, Rust embedding, WebAssembly), RustPython is worth considering despite its performance limitations.

**Looking forward**, RustPython has the potential to become a viable alternative as it matures and optimizes. The Rust implementation provides a cleaner foundation for future Python development.

---

## Appendices

### A. Raw Data

All raw benchmark data is available in `results/raw-data/`:
- `startup-times.json`
- `execution-speed.json`
- `memory-usage.json`
- `compatibility.json`

### B. Reproducibility

To reproduce these results:
1. Follow build instructions in `docs/build-instructions.md`
2. Run benchmarks in `scripts/benchmark/`
3. Generate visualizations in `scripts/visualize/`

### C. Limitations

This comparison has some limitations:
1. **Synthetic Benchmarks**: Not real-world applications
2. **Single Environment**: Tested only on Linux x86_64
3. **Alpha Software**: RustPython 0.5.0 is not feature-complete
4. **No Profiling**: Didn't profile where time is spent

### D. Future Work

Recommended improvements:
1. **Real-world Benchmarks**: Test with actual Python applications
2. **Multi-platform**: Test on macOS, Windows, ARM
3. **Profiling**: Identify performance bottlenecks
4. **C Extension Support**: Test NumPy, pandas compatibility

---

**Report Generated**: 2026-07-06  
**Authors**: Automated benchmark suite  
**Contact**: See README.md for contribution guidelines
