"""
Performance Benchmarking Suite (CO2 & CO3).
Compares:
1. Linked List vs Python List (Array) for Head Insertion, Tail Insertion, and Traversal.
2. Searching Algorithms: Linear Search vs Binary Search across varying dataset sizes.
3. Sorting Algorithms: Bubble Sort vs Insertion Sort vs Merge Sort across varying dataset sizes.

Outputs tabular metrics and generates an empirical analysis report.
"""

import random
import time
from typing import Any, Dict, List, Tuple
from structures.linked_list import SinglyLinkedList
from models.student import Student
from algorithms.searching import (
    linear_search_linked_list,
    linear_search_list,
    binary_search,
)
from algorithms.sorting import (
    bubble_sort,
    insertion_sort,
    merge_sort,
)


def generate_mock_students(count: int, seed: int = 42) -> List[Student]:
    """Generates synthetic student records for reproducible benchmarking."""
    rng = random.Random(seed)
    departments = ["CSE", "ECE", "IT", "MECH", "CIVIL"]
    subjects_pool = ["DSA", "WebDev", "OS", "Maths", "DBMS"]

    students = []
    for i in range(1, count + 1):
        marks = {sub: round(rng.uniform(40.0, 99.0), 1) for sub in subjects_pool}
        s = Student(
            student_id=f"STU{i:05d}",
            name=f"Student_{i}",
            department=rng.choice(departments),
            semester=3,
            marks=marks,
        )
        students.append(s)
    return students


def benchmark_storage_structures(n: int = 5000) -> Dict[str, Any]:
    """
    CO2 Benchmark: Compare Singly Linked List vs Python List (Array)
    Measures:
    1. Head Insertion: O(1) in Linked List vs O(n) in Python List (list.insert(0))
    2. Tail Insertion: Append
    3. Traversal / Linear Search: Pointer chasing vs Cache-friendly contiguous array
    """
    mock_data = generate_mock_students(n)

    # 1. Head Insertion Benchmark
    # Singly Linked List insert_at_beginning
    ll_head = SinglyLinkedList()
    t0 = time.perf_counter()
    for s in mock_data:
        ll_head.insert_at_beginning(s)
    ll_head_time = (time.perf_counter() - t0) * 1000.0

    # Python List insert(0)
    py_list_head: List[Any] = []
    t0 = time.perf_counter()
    for s in mock_data:
        py_list_head.insert(0, s)
    py_head_time = (time.perf_counter() - t0) * 1000.0

    # 2. Sequential Search / Traversal
    # Target item near the tail
    target_id = f"STU{n:05d}"

    t0 = time.perf_counter()
    _, ll_comps = ll_head.search_by_id(target_id)
    ll_search_time = (time.perf_counter() - t0) * 1000.0

    t0 = time.perf_counter()
    py_comps = 0
    for s in py_list_head:
        py_comps += 1
        if s.student_id == target_id:
            break
    py_search_time = (time.perf_counter() - t0) * 1000.0

    return {
        "dataset_size": n,
        "head_insertion": {
            "linked_list_ms": round(ll_head_time, 3),
            "python_list_ms": round(py_head_time, 3),
            "ratio_py_to_ll": round(py_head_time / max(0.0001, ll_head_time), 2),
        },
        "search_traversal": {
            "linked_list_ms": round(ll_search_time, 4),
            "python_list_ms": round(py_search_time, 4),
            "comparisons": py_comps,
        },
    }


def benchmark_searching_algorithms(
    sizes: List[int] = [100, 500, 1000, 5000, 10000]
) -> List[Dict[str, Any]]:
    """
    CO3 Benchmark: Compare Linear Search vs Binary Search across dataset sizes.
    Tests searching for a target near the end (worst-case scenario).
    """
    results = []

    for size in sizes:
        students = generate_mock_students(size)
        # Binary search requires sorted array
        sorted_students = sorted(students, key=lambda s: s.student_id)

        # Target ID near end
        target_id = sorted_students[-2].student_id

        # Linear Search on Python List
        res_linear = linear_search_list(students, target_id, key_func=lambda s: s.student_id)

        # Binary Search on Sorted List
        res_binary = binary_search(sorted_students, target_id, key_func=lambda s: s.student_id)

        results.append({
            "size": size,
            "target": target_id,
            "linear_time_ms": round(res_linear.execution_time_ms, 5),
            "linear_comparisons": res_linear.comparisons,
            "binary_time_ms": round(res_binary.execution_time_ms, 5),
            "binary_comparisons": res_binary.comparisons,
            "speedup_factor": round(
                res_linear.execution_time_ms / max(0.000001, res_binary.execution_time_ms), 2
            ),
        })

    return results


def benchmark_sorting_algorithms(
    sizes: List[int] = [100, 300, 700, 1500]
) -> List[Dict[str, Any]]:
    """
    CO3 Benchmark: Compare Bubble Sort, Insertion Sort, and Merge Sort
    across varying dataset sizes (sorting by marks descending).
    """
    results = []

    for size in sizes:
        data = generate_mock_students(size, seed=123)

        res_bubble = bubble_sort(data, criterion="marks", reverse=True)
        res_insertion = insertion_sort(data, criterion="marks", reverse=True)
        res_merge = merge_sort(data, criterion="marks", reverse=True)

        results.append({
            "size": size,
            "bubble": {
                "time_ms": round(res_bubble.execution_time_ms, 3),
                "comparisons": res_bubble.comparisons,
                "swaps": res_bubble.swaps_or_shifts,
            },
            "insertion": {
                "time_ms": round(res_insertion.execution_time_ms, 3),
                "comparisons": res_insertion.comparisons,
                "shifts": res_insertion.swaps_or_shifts,
            },
            "merge": {
                "time_ms": round(res_merge.execution_time_ms, 3),
                "comparisons": res_merge.comparisons,
                "moves": res_merge.swaps_or_shifts,
            },
        })

    return results


def generate_benchmark_summary_text() -> str:
    """Generate a formatted terminal text report of all benchmarks."""
    lines = []
    lines.append("=" * 80)
    lines.append("  ALGORITHM & DATA STRUCTURE PERFORMANCE BENCHMARK REPORT (CO2 & CO3)")
    lines.append("=" * 80)

    # 1. Storage Comparison
    lines.append("\n[1] DATA STRUCTURE COMPARISON: Singly Linked List vs Python List (Array)")
    lines.append("-" * 80)
    storage_res = benchmark_storage_structures(n=4000)
    hi = storage_res["head_insertion"]
    lines.append(f"  Dataset Size: {storage_res['dataset_size']} records")
    lines.append(f"  Head Insertion (Insert at Index 0):")
    lines.append(f"    - Singly Linked List: {hi['linked_list_ms']} ms  [O(1) pointer updates]")
    lines.append(f"    - Python List (Array): {hi['python_list_ms']} ms  [O(n) memory element shifting]")
    lines.append(f"    -> Linked List Head Insertion Speedup: {hi['ratio_py_to_ll']}x faster!")
    lines.append("\n  Technical Takeaway (CO2):")
    lines.append("    Linked Lists excel at O(1) front insertions without element relocation.")
    lines.append("    Python arrays suffer O(n) penalty because all downstream elements shift.")

    # 2. Searching Comparison
    lines.append("\n\n[2] SEARCHING COMPARISON: Linear Search vs Binary Search")
    lines.append("-" * 80)
    lines.append(f"{'Size (N)':<10} | {'Linear Comps':<14} | {'Linear Time':<14} | {'Binary Comps':<14} | {'Binary Time':<14} | {'Speedup':<10}")
    lines.append("-" * 80)
    search_res = benchmark_searching_algorithms([100, 500, 1000, 3000, 7000])
    for r in search_res:
        lines.append(
            f"{r['size']:<10} | {r['linear_comparisons']:<14} | {r['linear_time_ms']:>8.4f} ms    | "
            f"{r['binary_comparisons']:<14} | {r['binary_time_ms']:>8.4f} ms    | {r['speedup_factor']:>6.1f}x"
        )
    lines.append("\n  Technical Takeaway (CO3):")
    lines.append("    Binary Search achieves logarithmic O(log n) efficiency compared to O(n).")
    lines.append("    For N=7000, Linear Search tests ~7000 elements, while Binary Search takes <= 13!")

    # 3. Sorting Comparison
    lines.append("\n\n[3] SORTING COMPARISON: Bubble Sort vs Insertion Sort vs Merge Sort")
    lines.append("-" * 80)
    lines.append(f"{'Size (N)':<10} | {'Bubble Time':<16} | {'Insertion Time':<16} | {'Merge Sort Time':<16}")
    lines.append("-" * 80)
    sort_res = benchmark_sorting_algorithms([100, 300, 700, 1200])
    for r in sort_res:
        lines.append(
            f"{r['size']:<10} | {r['bubble']['time_ms']:>10.2f} ms     | "
            f"{r['insertion']['time_ms']:>10.2f} ms     | {r['merge']['time_ms']:>10.2f} ms"
        )
    lines.append("\n  Technical Takeaway (CO3):")
    lines.append("    Merge Sort O(n log n) outclasses O(n^2) quadratic algorithms as N grows.")
    lines.append("    Insertion Sort has lower constant factors than Bubble Sort, making it faster on small sets.")
    lines.append("=" * 80)

    return "\n".join(lines)
