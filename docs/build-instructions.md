# Build Instructions

This document provides detailed instructions for building both CPython and RustPython from source.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Building CPython](#building-cpython)
3. [Building RustPython](#building-rustpython)
4. [Troubleshooting](#troubleshooting)
5. [Verification](#verification)

---

## Prerequisites

### Common Requirements

- **Git**: For cloning repositories
- **Internet Connection**: For downloading dependencies
- **Disk Space**: At least 10GB free space
- **RAM**: 8GB+ recommended

### CPython Requirements

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libreadline-dev \
    libffi-dev \
    libsqlite3-dev \
    wget \
    libbz2-dev \
    liblzma-dev \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    libcurl4-openssl-dev
```

#### macOS
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install Homebrew dependencies
brew install openssl readline sqlite3 xz zlib tk
```

#### Windows
```bash
# Install Visual Studio Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
# Select "Desktop development with C++" workload
```

### RustPython Requirements

#### Install Rust
```bash
# Install Rust using rustup
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Follow the prompts and restart your shell
source $HOME/.cargo/env

# Update to latest stable
rustup update stable
```

#### Verify Rust Installation
```bash
rustc --version  # Should be 1.95.0 or higher
cargo --version
```

---

## Building CPython

### 1. Clone the Repository

```bash
git clone https://github.com/python/cpython.git
cd cpython
```

### 2. Checkout the Correct Version

For this project, we use CPython 3.14.0:

```bash
git fetch --tags
git checkout v3.14.0
```

### 3. Configure the Build

#### Basic Build
```bash
./configure
```

#### Optimized Build (Recommended)
```bash
./configure --enable-optimizations --with-lto
```

Options explained:
- `--enable-optimizations`: Enables Profile Guided Optimization (PGO)
- `--with-lto`: Enables Link Time Optimization
- `--prefix=/path/to/install`: Specify custom install path
- `--with-pydebug`: Build with debug symbols (for development)

### 4. Compile

```bash
make -j$(nproc)
```

This will take 5-10 minutes depending on your system.

### 5. Verify the Build

```bash
./python --version
# Should output: Python 3.14.0
```

### 6. Run Tests (Optional)

```bash
make test
```

---

## Building RustPython

### 1. Clone the Repository

```bash
git clone https://github.com/RustPython/RustPython.git
cd RustPython
```

### 2. Verify Rust Version

RustPython requires Rust 1.95.0+:

```bash
rustc --version
# Should be 1.95.0 or higher
```

If not, update:
```bash
rustup update stable
```

### 3. Build in Release Mode

```bash
cargo build --release
```

This will take 5-15 minutes for the first build (downloads dependencies).

### 4. Verify the Build

```bash
./target/release/rustpython --version
# Should output: Python 3.14.0.alpha (RustPython 0.5.0)
```

### 5. Build with Additional Features (Optional)

#### With JIT Compiler
```bash
cargo build --release --features jit
```

Requires: `autoconf`, `automake`, `libtool`, `clang`

#### With SSL Support
```bash
cargo build --release --features ssl-rustls-aws-lc
```

#### For WebAssembly
```bash
rustup target add wasm32-wasip1
cargo build --target wasm32-wasip1 --no-default-features --features freeze-stdlib,stdlib
```

---

## Troubleshooting

### CPython Issues

#### Error: `configure: error: no acceptable C compiler found`
**Solution**: Install build tools
```bash
# Ubuntu/Debian
sudo apt-get install build-essential

# macOS
xcode-select --install
```

#### Error: `ModuleNotFoundError: No module named '_ssl'`
**Solution**: Install OpenSSL development packages
```bash
# Ubuntu/Debian
sudo apt-get install libssl-dev

# macOS
brew install openssl
export LDFLAGS="-L$(brew --prefix openssl)/lib"
export CPPFLAGS="-I$(brew --prefix openssl)/include"
```

#### Error: `zlib not available`
**Solution**: Install zlib
```bash
sudo apt-get install zlib1g-dev
```

### RustPython Issues

#### Error: `rustc 1.92.0 is not supported`
**Solution**: Update Rust
```bash
rustup update stable
```

#### Error: `error[E0308]: mismatched types`
**Solution**: Clean and rebuild
```bash
cargo clean
cargo build --release
```

#### Error: `can't find crate for `std``
**Solution**: Reinstall Rust toolchain
```bash
rustup toolchain install stable --force
```

---

## Verification

After building both implementations, verify they work correctly:

### Test CPython
```bash
cd /path/to/cpython
./python -c "print('Hello from CPython!')"
./python -c "import sys; print(sys.version)"
```

### Test RustPython
```bash
cd /path/to/RustPython
./target/release/rustpython -c "print('Hello from RustPython!')"
./target/release/rustpython -c "import sys; print(sys.version)"
```

### Run Basic Benchmark
```bash
time ./python -c "pass"
time ./target/release/rustpython -c "pass"
```

---

## Quick Build Script

For convenience, here's a script to build both:

```bash
#!/bin/bash
# build-all.sh

set -e

echo "=== Building CPython 3.14.0 ==="
git clone --depth 1 https://github.com/python/cpython.git
cd cpython
git fetch --tags
git checkout v3.14.0
./configure --enable-optimizations
make -j$(nproc)
echo "CPython built successfully!"
cd ..

echo "=== Building RustPython ==="
git clone --depth 1 https://github.com/RustPython/RustPython.git
cd RustPython
cargo build --release
echo "RustPython built successfully!"
cd ..

echo "=== Build Complete ==="
```

Save this as `build-all.sh` and run:
```bash
chmod +x build-all.sh
./build-all.sh
```

---

## Next Steps

After building both implementations:

1. Run the benchmarks: `python3 scripts/benchmark/startup_benchmark.py`
2. Generate visualizations: `python3 scripts/visualize/generate_charts.py`
3. View results in `results/` directory

---

## References

- CPython Build Instructions: https://devguide.python.org/setup/
- RustPython README: https://github.com/RustPython/RustPython/blob/main/README.md
- Rust Installation: https://www.rust-lang.org/tools/install
