"""
Sorting Algorithms Implementation (CO3).
Includes:
1. Bubble Sort: O(n^2) comparison-based sort with early-termination optimization.
2. Insertion Sort: O(n^2) incremental sort with low constant factors, optimal for small sets.
3. Merge Sort: O(n log n) divide-and-conquer stable sort.

Collects empirical metrics: wall-clock runtime (ms), comparison counter, and swap/move operations.
"""

import time
from dataclasses import dataclass
from typing import Any, Callable, List


@dataclass
class SortResult:
    """Holds sorted list and empirical performance statistics."""
    sorted_items: List[Any]
    comparisons: int
    swaps_or_moves: int
    execution_time_ms: float
    algorithm: str


def bubble_sort(
    arr: List[Any],
    key_func: Callable[[Any], Any] = lambda x: x,
    reverse: bool = False,
) -> SortResult:
    """
    Bubble Sort Implementation.
    Repeatedly steps through list, compares adjacent elements, and swaps if misordered.
    Includes early-termination flag if no swap occurs in a pass.

    Time Complexity:
      - Best Case: O(n) [already sorted]
      - Worst Case: O(n^2) [reverse sorted]
      - Average Case: O(n^2)
    Space Complexity: O(1) auxiliary
    """
    items = list(arr)
    n = len(items)
    comparisons = 0
    swaps = 0

    start = time.perf_counter()

    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            comparisons += 1
            val_a = key_func(items[j])
            val_b = key_func(items[j + 1])

            condition = (val_a < val_b) if reverse else (val_a > val_b)
            if condition:
                items[j], items[j + 1] = items[j + 1], items[j]
                swaps += 1
                swapped = True

        if not swapped:
            break

    elapsed_ms = (time.perf_counter() - start) * 1000.0

    return SortResult(
        sorted_items=items,
        comparisons=comparisons,
        swaps_or_moves=swaps,
        execution_time_ms=elapsed_ms,
        algorithm="Bubble Sort",
    )


def insertion_sort(
    arr: List[Any],
    key_func: Callable[[Any], Any] = lambda x: x,
    reverse: bool = False,
) -> SortResult:
    """
    Insertion Sort Implementation.
    Builds sorted partition by shifting larger (or smaller) elements rightward.

    Time Complexity:
      - Best Case: O(n) [already sorted]
      - Worst Case: O(n^2)
      - Average Case: O(n^2)
    Space Complexity: O(1) auxiliary
    """
    items = list(arr)
    n = len(items)
    comparisons = 0
    shifts = 0

    start = time.perf_counter()

    for i in range(1, n):
        key_item = items[i]
        key_val = key_func(key_item)
        j = i - 1

        while j >= 0:
            comparisons += 1
            curr_val = key_func(items[j])
            condition = (curr_val < key_val) if reverse else (curr_val > key_val)

            if condition:
                items[j + 1] = items[j]
                shifts += 1
                j -= 1
            else:
                break

        items[j + 1] = key_item

    elapsed_ms = (time.perf_counter() - start) * 1000.0

    return SortResult(
        sorted_items=items,
        comparisons=comparisons,
        swaps_or_moves=shifts,
        execution_time_ms=elapsed_ms,
        algorithm="Insertion Sort",
    )


def merge_sort(
    arr: List[Any],
    key_func: Callable[[Any], Any] = lambda x: x,
    reverse: bool = False,
) -> SortResult:
    """
    Merge Sort Implementation (Divide and Conquer).
    Recursively bisects array, sorts sub-arrays, and merges them.

    Time Complexity:
      - Best Case: O(n log n)
      - Worst Case: O(n log n)
      - Average Case: O(n log n)
    Space Complexity: O(n) auxiliary
    """
    items = list(arr)
    comparisons = 0
    moves = 0

    start = time.perf_counter()

    def _merge_sort_rec(sub_arr: List[Any]) -> List[Any]:
        nonlocal comparisons, moves
        if len(sub_arr) <= 1:
            return sub_arr

        mid = len(sub_arr) // 2
        left = _merge_sort_rec(sub_arr[:mid])
        right = _merge_sort_rec(sub_arr[mid:])

        merged = []
        i = j = 0

        while i < len(left) and j < len(right):
            comparisons += 1
            val_l = key_func(left[i])
            val_r = key_func(right[j])

            condition = (val_l >= val_r) if reverse else (val_l <= val_r)
            if condition:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1
            moves += 1

        while i < len(left):
            merged.append(left[i])
            i += 1
            moves += 1

        while j < len(right):
            merged.append(right[j])
            j += 1
            moves += 1

        return merged

    sorted_res = _merge_sort_rec(items)
    elapsed_ms = (time.perf_counter() - start) * 1000.0

    return SortResult(
        sorted_items=sorted_res,
        comparisons=comparisons,
        swaps_or_moves=moves,
        execution_time_ms=elapsed_ms,
        algorithm="Merge Sort",
    )
