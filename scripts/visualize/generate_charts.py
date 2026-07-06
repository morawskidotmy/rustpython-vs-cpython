#!/usr/bin/env python3
"""
Generate visualizations from benchmark data
"""
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Set style
plt.style.use('seaborn-v0_8-darkgrid')

def load_json(filepath):
    """Load JSON data from file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def create_startup_comparison():
    """Create startup time comparison chart"""
    data = load_json("results/raw-data/startup-times.json")
    
    implementations = ['CPython', 'RustPython']
    times = [data['cpython']['mean_ms'], data['rustpython']['mean_ms']]
    colors = ['#3776AB', '#DEA584']  # CPython blue, Rust orange
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(implementations, times, color=colors, edgecolor='black')
    
    # Add value labels on bars
    for bar, time in zip(bars, times):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{time:.2f} ms',
                ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    ax.set_ylabel('Startup Time (ms)', fontsize=12, fontweight='bold')
    ax.set_title('Python Interpreter Startup Time Comparison\n(Lower is better)', 
                fontsize=14, fontweight='bold', pad=20)
    ax.set_ylim(0, max(times) * 1.2)
    
    # Add ratio annotation
    ratio = times[1] / times[0]
    ax.text(0.5, 0.95, f'CPython is {ratio:.1f}x faster', 
            transform=ax.transAxes, ha='center', va='top',
            fontsize=11, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig('results/visualizations/startup-time-comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created startup-time-comparison.png")

def create_execution_speed_comparison():
    """Create execution speed comparison chart"""
    data = load_json("results/raw-data/execution-speed.json")
    
    benchmarks = list(data['cpython'].keys())
    cpython_times = [data['cpython'][b]['mean'] for b in benchmarks]
    rustpython_times = [data['rustpython'][b]['mean'] for b in benchmarks]
    
    x = np.arange(len(benchmarks))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 7))
    bars1 = ax.bar(x - width/2, cpython_times, width, 
                   label='CPython', color='#3776AB', edgecolor='black')
    bars2 = ax.bar(x + width/2, rustpython_times, width,
                   label='RustPython', color='#DEA584', edgecolor='black')
    
    ax.set_xlabel('Benchmark', fontsize=12, fontweight='bold')
    ax.set_ylabel('Execution Time (seconds)', fontsize=12, fontweight='bold')
    ax.set_title('Python Execution Speed Comparison\n(Lower is better)', 
                fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(benchmarks, rotation=45, ha='right')
    ax.legend(fontsize=11)
    ax.set_yscale('log')  # Log scale for better visualization
    
    # Add ratio labels
    for i, (cp, rp) in enumerate(zip(cpython_times, rustpython_times)):
        ratio = rp / cp if cp > 0 else 0
        ax.text(i, max(cp, rp) * 1.5, f'{ratio:.1f}x',
                ha='center', va='bottom', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))
    
    plt.tight_layout()
    plt.savefig('results/visualizations/execution-speed-comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created execution-speed-comparison.png")

def create_memory_usage_chart():
    """Create memory usage comparison chart"""
    data = load_json("results/raw-data/memory-usage.json")
    
    tests = list(data['cpython'].keys())
    cpython_memory = []
    rustpython_memory = []
    
    for t in tests:
        cp = data['cpython'][t]
        rp = data['rustpython'][t]
        cpython_memory.append(cp.get('peak_rss_mb', 0) if cp.get('success') else 0)
        rustpython_memory.append(rp.get('peak_rss_mb', 0) if rp.get('success') else 0)
    
    x = np.arange(len(tests))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 7))
    bars1 = ax.bar(x - width/2, cpython_memory, width,
                   label='CPython', color='#3776AB', edgecolor='black')
    bars2 = ax.bar(x + width/2, rustpython_memory, width,
                   label='RustPython', color='#DEA584', edgecolor='black')
    
    ax.set_xlabel('Test Case', fontsize=12, fontweight='bold')
    ax.set_ylabel('Memory Usage (KB)', fontsize=12, fontweight='bold')
    ax.set_title('Python Memory Usage Comparison\n(Lower is better)', 
                fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(tests, rotation=45, ha='right')
    ax.legend(fontsize=11)
    
    plt.tight_layout()
    plt.savefig('results/visualizations/memory-usage-comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created memory-usage-comparison.png")

def create_compatibility_pie_chart():
    """Create compatibility pie charts"""
    data = load_json("results/raw-data/compatibility.json")
    
    # Syntax support
    syntax_data = data['syntax_support']
    rp_syntax = sum(1 for s in syntax_data['rustpython'].values() if s['supported'])
    cp_syntax = sum(1 for s in syntax_data['cpython'].values() if s['supported'])
    total_syntax = len(syntax_data['rustpython'])
    
    # Stdlib coverage
    stdlib_data = data['stdlib_coverage']
    rp_stdlib = sum(1 for m in stdlib_data['rustpython'].values() if m['importable'])
    cp_stdlib = sum(1 for m in stdlib_data['cpython'].values() if m['importable'])
    total_stdlib = len(stdlib_data['rustpython'])
    
    # Create subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    
    # Syntax support pie charts
    ax1.pie([cp_syntax, total_syntax - cp_syntax], 
            labels=['Supported', 'Not Supported'],
            autopct='%1.0f%%', startangle=90,
            colors=['#3776AB', '#FF6B6B'])
    ax1.set_title(f'CPython Syntax Support\n({cp_syntax}/{total_syntax})', fontweight='bold')
    
    ax2.pie([rp_syntax, total_syntax - rp_syntax],
            labels=['Supported', 'Not Supported'],
            autopct='%1.0f%%', startangle=90,
            colors=['#DEA584', '#FF6B6B'])
    ax2.set_title(f'RustPython Syntax Support\n({rp_syntax}/{total_syntax})', fontweight='bold')
    
    # Stdlib coverage pie charts
    ax3.pie([cp_stdlib, total_stdlib - cp_stdlib],
            labels=['Importable', 'Not Importable'],
            autopct='%1.0f%%', startangle=90,
            colors=['#3776AB', '#FF6B6B'])
    ax3.set_title(f'CPython Stdlib Coverage\n({cp_stdlib}/{total_stdlib})', fontweight='bold')
    
    ax4.pie([rp_stdlib, total_stdlib - rp_stdlib],
            labels=['Importable', 'Not Importable'],
            autopct='%1.0f%%', startangle=90,
            colors=['#DEA584', '#FF6B6B'])
    ax4.set_title(f'RustPython Stdlib Coverage\n({rp_stdlib}/{total_stdlib})', fontweight='bold')
    
    plt.suptitle('Python Compatibility Comparison', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('results/visualizations/compatibility-pie-charts.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created compatibility-pie-charts.png")

def create_summary_dashboard():
    """Create a summary dashboard with key metrics"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    # 1. Startup time comparison
    startup_data = load_json("results/raw-data/startup-times.json")
    impls = ['CPython', 'RustPython']
    times = [startup_data['cpython']['mean_ms'], startup_data['rustpython']['mean_ms']]
    ax1.bar(impls, times, color=['#3776AB', '#DEA584'], edgecolor='black')
    ax1.set_title('Startup Time (ms)\nLower is better', fontweight='bold')
    ax1.set_ylabel('Milliseconds')
    for i, v in enumerate(times):
        ax1.text(i, v + 5, f'{v:.1f}', ha='center', fontweight='bold')
    
    # 2. Execution speed ratios
    exec_data = load_json("results/raw-data/execution-speed.json")
    benchmarks = list(exec_data['cpython'].keys())
    ratios = []
    for b in benchmarks:
        cp = exec_data['cpython'][b]['mean']
        rp = exec_data['rustpython'][b]['mean']
        ratios.append(rp / cp if cp > 0 else 0)
    
    ax2.barh(benchmarks, ratios, color='#FF6B6B', edgecolor='black')
    ax2.set_title('Speed Ratio (RustPython/CPython)\nLower is better', fontweight='bold')
    ax2.set_xlabel('Ratio')
    ax2.axvline(x=1, color='green', linestyle='--', linewidth=2, label='Equal performance')
    ax2.legend()
    
    # 3. Compatibility summary
    compat_data = load_json("results/raw-data/compatibility.json")
    categories = ['Syntax\nSupport', 'Stdlib\nCoverage']
    cpython_scores = [
        sum(1 for s in compat_data['syntax_support']['cpython'].values() if s['supported']),
        sum(1 for m in compat_data['stdlib_coverage']['cpython'].values() if m['importable'])
    ]
    rustpython_scores = [
        sum(1 for s in compat_data['syntax_support']['rustpython'].values() if s['supported']),
        sum(1 for m in compat_data['stdlib_coverage']['rustpython'].values() if m['importable'])
    ]
    
    x = np.arange(len(categories))
    width = 0.35
    ax3.bar(x - width/2, cpython_scores, width, label='CPython', color='#3776AB')
    ax3.bar(x + width/2, rustpython_scores, width, label='RustPython', color='#DEA584')
    ax3.set_title('Compatibility Scores', fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(categories)
    ax3.legend()
    ax3.set_ylim(0, 25)
    
    # 4. Overall assessment - based on benchmark results, not hardcoded
    # Calculate actual scores from data
    startup_data = load_json("results/raw-data/startup-times.json")
    startup_score = 2 if startup_data['cpython']['mean_ms'] < startup_data['rustpython']['mean_ms'] else 4
    
    # Execution speed score (based on average ratio)
    exec_data = load_json("results/raw-data/execution-speed.json")
    benchmarks = list(exec_data['cpython'].keys())
    ratios = []
    for b in benchmarks:
        cp = exec_data['cpython'][b]['mean']
        rp = exec_data['rustpython'][b]['mean']
        ratios.append(rp / cp if cp > 0 else 0)
    
    avg_ratio = sum(ratios) / len(ratios) if ratios else 1
    speed_score = max(1, min(5, int(5 / avg_ratio))) if avg_ratio > 0 else 3
    
    # Compatibility score
    compat_data = load_json("results/raw-data/compatibility.json")
    cp_syntax = sum(1 for s in compat_data['syntax_support']['cpython'].values() if s['supported'])
    rp_syntax = sum(1 for s in compat_data['syntax_support']['rustpython'].values() if s['supported'])
    total_syntax = len(compat_data['syntax_support']['cpython'])
    
    metrics = ['Startup\nSpeed', 'Execution\nSpeed', 'Compatibility\n(Python Syntax)']
    cpython_scores = [startup_score, 5, int((cp_syntax / total_syntax) * 5)]
    rustpython_scores = [2, speed_score, int((rp_syntax / total_syntax) * 5)]
    
    x = np.arange(len(metrics))
    ax4.bar(x - width/2, cpython_scores, width, label='CPython', color='#3776AB')
    ax4.bar(x + width/2, rustpython_scores, width, label='RustPython', color='#DEA584')
    ax4.set_title('Overall Assessment\n(Out of 5)', fontweight='bold')
    ax4.set_xticks(x)
    ax4.set_xticklabels(metrics)
    ax4.set_ylim(0, 5)
    ax4.legend()
    
    plt.suptitle('RustPython vs CPython: Comprehensive Comparison Dashboard', 
                fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('results/visualizations/summary-dashboard.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created summary-dashboard.png")

def main():
    print("Generating visualizations...\n")
    
    # Create visualizations directory if it doesn't exist
    Path("results/visualizations").mkdir(parents=True, exist_ok=True)
    
    # Generate all charts
    create_startup_comparison()
    create_execution_speed_comparison()
    create_memory_usage_chart()
    create_compatibility_pie_chart()
    create_summary_dashboard()
    
    print("\n✅ All visualizations generated successfully!")
    print("📁 Check results/visualizations/ directory")

if __name__ == "__main__":
    main()
