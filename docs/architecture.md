# Architecture and Comparison Methodology

This document describes the architectural differences between CPython and RustPython, and the methodology used for comparison.

## Table of Contents

1. [CPython Architecture](#cpython-architecture)
2. [RustPython Architecture](#rustpython-architecture)
3. [Key Differences](#key-differences)
4. [Comparison Framework](#comparison-framework)

---

## CPython Architecture

### Overview

CPython is the reference implementation of Python, written in C. It's been in development since 1989 (over 30 years).

### Components

#### 1. Parser
- **Purpose**: Convert Python source code to Abstract Syntax Tree (AST)
- **Implementation**: Hand-written parser in C (formerly pgen, now peg_parser)
- **Output**: Python AST (defined in `Parser/`)

#### 2. Compiler
- **Purpose**: Compile AST to bytecode
- **Implementation**: C code in `Python/compiler.c`
- **Output**: Python bytecode (`.pyc` files)

#### 3. Virtual Machine (VM)
- **Purpose**: Execute Python bytecode
- **Implementation**: Stack-based interpreter in `Python/ceval.c`
- **Features**:
  - GIL (Global Interpreter Lock)
  - Reference counting + cyclic GC
  - Frame objects for function calls

#### 4. Object Model
- **Purpose**: Define Python objects in C
- **Implementation**: `Objects/` directory
- **Key Types**: `PyObject`, `PyTypeObject`, `PyLongObject`, etc.

#### 5. Standard Library
- **Pure Python**: `Lib/` directory
- **C Extensions**: `Modules/` directory
- **Built-in Modules**: Compiled into the interpreter

### Memory Management

#### Reference Counting
- Each object has a reference count
- When count reaches 0, object is deallocated
- Fast but doesn't handle circular references

#### Cyclic Garbage Collector
- Handles circular references
- Runs periodically
- Implemented in `Modules/gcmodule.c`

#### Memory Allocator
- `PyMem_Malloc()`, `PyMem_Free()`
- Custom allocators for small objects
- Arena-based allocation

### Execution Flow

```
Source Code (.py)
    ↓
Parser (tokenizer + parser)
    ↓
AST (Abstract Syntax Tree)
    ↓
Compiler (AST → Bytecode)
    ↓
Code Objects (.pyc files)
    ↓
Virtual Machine (executes bytecode)
    ↓
Results
```

---

## RustPython Architecture

### Overview

RustPython is a Python 3.14 interpreter written in Rust. It's a newer project (started ~2017) and currently at version 0.5.0 (alpha).

### Components

#### 1. Parser
- **Purpose**: Parse Python source code
- **Implementation**: Written in Rust, uses `rustpython-compiler`
- **Dependencies**: Uses modified Ruff parser for some parts
- **Output**: Rust representation of Python AST

#### 2. Compiler
- **Purpose**: Compile AST to bytecode
- **Implementation**: `rustpython-compiler` crate
- **Output**: RustPython bytecode (similar to CPython)

#### 3. Virtual Machine (VM)
- **Purpose**: Execute bytecode
- **Implementation**: `rustpython-vm` crate
- **Features**:
  - No GIL (potential for parallelism)
  - Rust's ownership model for memory safety
  - Frame-based execution

#### 4. Object Model
- **Purpose**: Define Python objects in Rust
- **Implementation**: `rustpython-common` and `rustpython-vm` crates
- **Key Types**: `PyObject`, `PyType`, `PyInt`, etc.

#### 5. Standard Library
- **Pure Python**: Copied from CPython's `Lib/`
- **Rust Implementations**: `rustpython-stdlib` crate
- **Limitations**: Some modules not fully implemented

### Memory Management

#### Rust Ownership
- Memory safety guaranteed by Rust's ownership model
- No manual memory management needed
- Reference counting via `Rc<>` and `Arc<>`

#### Garbage Collection
- Optional GC via `rustpython-vm`
- Not as mature as CPython's GC
- May use reference counting primarily

### Execution Flow

```
Source Code (.py)
    ↓
Parser (in Rust)
    ↓
AST (Rust structs)
    ↓
Compiler (AST → Bytecode)
    ↓
Code Objects
    ↓
Virtual Machine (executes bytecode)
    ↓
Results
```

---

## Key Differences

### 1. Language

| Aspect | CPython | RustPython |
|--------|----------|------------|
| Implementation Language | C | Rust |
| Memory Safety | Manual (prone to bugs) | Guaranteed by compiler |
| Concurrency | GIL (single-threaded) | No GIL (potential parallelism) |
| Undefined Behavior | Possible | Impossible (in safe Rust) |

### 2. Performance

| Aspect | CPython | RustPython |
|--------|----------|------------|
| Startup Time | Fast (~27ms) | Slower (~128ms) |
| Execution Speed | Fast (optimized) | Slower (3-7x) |
| Memory Usage | Low | Moderate |
| JIT Compilation | Experimental (3.13+) | Experimental |

### 3. Maturity

| Aspect | CPython | RustPython |
|--------|----------|------------|
| Age | 30+ years | 7+ years |
| Version | 3.14.0 (stable) | 0.5.0 (alpha) |
| Test Coverage | Extensive | Growing |
| Production Use | Widely used | Limited |

### 4. Standard Library

| Aspect | CPython | RustPython |
|--------|----------|------------|
| Pure Python Modules | Complete | Mostly complete |
| C Extension Modules | Complete | Partial |
| Third-party Support | Full | Limited |

### 5. Platform Support

| Aspect | CPython | RustPython |
|--------|----------|------------|
| Desktop Platforms | All major | Most (via Rust) |
| Mobile Platforms | Limited | Possible (via Rust) |
| WebAssembly | Experimental | Native support |
| Embedding | Possible (C API) | Easy (Rust crate) |

---

## Comparison Framework

### Dimensions of Comparison

#### 1. Performance
- **Startup Time**: How fast does the interpreter start?
- **Execution Speed**: How fast does code run?
- **Memory Usage**: How much memory is used?

#### 2. Compatibility
- **Syntax Support**: Does it support Python 3.14 syntax?
- **Stdlib Coverage**: How many stdlib modules work?
- **C Extension Support**: Can it load C extensions?

#### 3. Development Experience
- **Build Time**: How long to compile?
- **Code Quality**: How maintainable is the codebase?
- **Debugging**: How easy is it to debug?

#### 4. Deployment
- **Binary Size**: How large is the executable?
- **Dependencies**: What system libraries are needed?
- **Cross-compilation**: How easy is it to target other platforms?

### Metrics Collection

#### Automated Benchmarks
- Scripts in `scripts/benchmark/`
- Run multiple times for statistical significance
- Store results as JSON

#### Manual Testing
- Interactive REPL testing
- Real-world script execution
- Edge case exploration

#### Documentation Review
- Compare feature lists
- Review known limitations
- Check issue trackers

### Analysis Approach

#### Quantitative Analysis
- Statistical comparison of benchmark results
- Speedup/slowdown ratios
- Memory usage comparisons

#### Qualitative Analysis
- Code review (where applicable)
- Documentation comparison
- Community feedback

#### Visualization
- Charts and graphs for easy comparison
- Dashboard for high-level overview
- Detailed reports for specifics

---

## Architectural Implications

### Why CPython is Faster (Currently)

1. **C Implementation**: Direct memory access, no safety checks
2. **30 Years of Optimization**: Highly tuned code paths
3. **Mature JIT**: Experimental JIT in CPython 3.13+
4. **Memory Layout**: Optimized object layout for Python's needs

### Why RustPython Might Be Better (Eventually)

1. **Memory Safety**: No segfaults, buffer overflows, etc.
2. **No GIL**: Potential for true parallelism
3. **Modern Design**: Cleaner architecture, easier to optimize
4. **WebAssembly**: First-class WASM support
5. **Rust Ecosystem**: Can leverage Rust crates for performance

### Trade-offs

| Decision | CPython | RustPython |
|----------|----------|------------|
| Safety vs Speed | Speed (unsafe C) | Safety (safe Rust) |
| Maturity vs Modernity | Mature (old codebase) | Modern (new codebase) |
| GIL vs No GIL | GIL (simpler) | No GIL (complex) |
| C Extensions vs Pure Python | C extensions (fast) | Pure Python/Rust (safer) |

---

## Future Directions

### CPython

- **No GIL**: PEP 703 (gradual rollout)
- **Better JIT**: PEP 659 (adaptive interpreter)
- **Faster Startup**: PEP 660 (editable installs)
- **Better Embedding**: Improved C API

### RustPython

- **Performance Optimization**: Need significant work
- **Completion**: Finish implementing all Python features
- **C Extension Support**: Critical for scientific computing
- **WASM Improvements**: Better browser integration

---

## Conclusion

Both implementations have their strengths:

- **CPython**: Production-ready, fast, full compatibility
- **RustPython**: Memory-safe, modern, potential for future optimization

The choice depends on your needs:
- Use **CPython** for production, performance-critical applications
- Use **RustPython** for safety-critical applications, embedding in Rust, or WebAssembly targets

---

## References

- CPython Internals: https://realpython.com/cpython-source-code-guide/
- RustPython Architecture: https://rustpython.github.io/
- Python AST: https://docs.python.org/3/library/ast.html
- Rust Ownership: https://doc.rust-lang.org/book/ch04-00-understanding-ownership.html
