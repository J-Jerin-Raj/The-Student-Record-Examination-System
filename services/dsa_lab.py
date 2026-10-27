"""
Interactive DSA Performance Lab Service (CO2 & CO3).
Generates benchmark data across dataset sizes (100 to 5,000 items)
to compare searching and sorting algorithms empirically.
"""

import random
import time
from typing import Any, Dict, List
from algorithms.searching import linear_search, binary_search
from algorithms.sorting import bubble_sort, insertion_sort, merge_sort
from data_structures.linked_list import SinglyLinkedList


class DSALabService:
    """Runs empirical benchmark trials on searching, sorting, and linked list operations."""

    @staticmethod
    def generate_random_dataset(size: int, seed: int = 42) -> List[int]:
        """Generate a reproducible random array of integers."""
        rng = random.Random(seed)
        return [rng.randint(1, 100000) for _ in range(size)]

    @staticmethod
    def run_searching_benchmark(size: int = 1000) -> Dict[str, Any]:
        """
        Compare Linear Search vs Binary Search on dataset of given size.
        Target item placed near the end for worst-case analysis.
        """
        arr = DSALabService.generate_random_dataset(size)
        sorted_arr = sorted(arr)
        target = sorted_arr[-3] if size >= 3 else sorted_arr[-1]

        # 1. Linear Search on Array
        res_linear = linear_search(arr, target)

        # 2. Binary Search on Sorted Array
        res_binary = binary_search(sorted_arr, target)

        # 3. Linear Search on Singly Linked List
        ll = SinglyLinkedList()
        for x in arr:
            ll.insert_rear(x)

        t0 = time.perf_counter()
        _, ll_comps = ll.search_by_id(str(target))
        ll_time_ms = (time.perf_counter() - t0) * 1000.0

        return {
            "dataset_size": size,
            "target": target,
            "linear_array": {
                "comparisons": res_linear.comparisons,
                "time_ms": round(res_linear.execution_time_ms, 5),
                "complexity": "O(n)",
            },
            "binary_search": {
                "comparisons": res_binary.comparisons,
                "time_ms": round(res_binary.execution_time_ms, 5),
                "complexity": "O(log n)",
            },
            "linked_list_search": {
                "comparisons": ll_comps,
                "time_ms": round(ll_time_ms, 5),
                "complexity": "O(n)",
            },
            "speedup_factor": round(res_linear.execution_time_ms / max(0.000001, res_binary.execution_time_ms), 1),
        }

    @staticmethod
    def run_sorting_benchmark(size: int = 1000) -> Dict[str, Any]:
        """
        Compare Bubble Sort, Insertion Sort, and Merge Sort on equivalent dataset.
        For sizes > 2000, quadratic sorts may be scaled or limited to prevent long timeouts.
        """
        raw_arr = DSALabService.generate_random_dataset(size)

        # Run Merge Sort O(n log n)
        res_merge = merge_sort(raw_arr)

        # For N <= 2500 run Insertion Sort
        if size <= 3000:
            res_insertion = insertion_sort(raw_arr)
            insertion_data = {
                "time_ms": round(res_insertion.execution_time_ms, 3),
                "comparisons": res_insertion.comparisons,
                "swaps": res_insertion.swaps_or_moves,
                "complexity": "O(n^2)",
            }
        else:
            insertion_data = {"time_ms": "Skipped (>3000)", "comparisons": "-", "swaps": "-", "complexity": "O(n^2)"}

        # For N <= 1500 run Bubble Sort
        if size <= 1500:
            res_bubble = bubble_sort(raw_arr)
            bubble_data = {
                "time_ms": round(res_bubble.execution_time_ms, 3),
                "comparisons": res_bubble.comparisons,
                "swaps": res_bubble.swaps_or_moves,
                "complexity": "O(n^2)",
            }
        else:
            bubble_data = {"time_ms": "Skipped (>1500)", "comparisons": "-", "swaps": "-", "complexity": "O(n^2)"}

        return {
            "dataset_size": size,
            "bubble": bubble_data,
            "insertion": insertion_data,
            "merge": {
                "time_ms": round(res_merge.execution_time_ms, 3),
                "comparisons": res_merge.comparisons,
                "swaps": res_merge.swaps_or_moves,
                "complexity": "O(n log n)",
            },
        }

    @staticmethod
    def run_storage_benchmark(size: int = 3000) -> Dict[str, Any]:
        """
        CO2 Benchmark: Singly Linked List vs Python List (Array).
        Demonstrates O(1) head insertion on linked list vs O(n) element shifting on array.
        """
        data = DSALabService.generate_random_dataset(size)

        # Singly Linked List Head Insertion
        ll = SinglyLinkedList()
        t0 = time.perf_counter()
        for x in data:
            ll.insert_front(x)
        ll_head_time = (time.perf_counter() - t0) * 1000.0

        # Python Array Head Insertion list.insert(0, x)
        arr = []
        t0 = time.perf_counter()
        for x in data:
            arr.insert(0, x)
        arr_head_time = (time.perf_counter() - t0) * 1000.0

        ratio = round(arr_head_time / max(0.001, ll_head_time), 1)

        return {
            "dataset_size": size,
            "linked_list_head_insert_ms": round(ll_head_time, 3),
            "array_head_insert_ms": round(arr_head_time, 3),
            "speedup_ratio": ratio,
            "explanation": (
                f"Inserting {size} items at index 0 takes {round(ll_head_time, 2)} ms in Linked List "
                f"(re-linking pointer O(1)) vs {round(arr_head_time, 2)} ms in Array (shifting elements in memory O(n)). "
                f"Linked List head insertion is {ratio}x faster."
            ),
        }
