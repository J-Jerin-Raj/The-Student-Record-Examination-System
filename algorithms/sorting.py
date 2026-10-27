"""
Sorting Algorithms Implementation (CO3).
Includes:
1. Bubble Sort: Comparison-based O(n^2) sorting with early termination optimization.
2. Insertion Sort: Incremental O(n^2) sorting, highly efficient for small/nearly sorted data.
3. Merge Sort: Divide-and-conquer O(n log n) sorting, stable and predictable.

Supports dynamic sorting criteria:
- By Marks (total_marks or percentage)
- By Name (alphabetical)
- By Student ID (alphanumerical)
Supports both Ascending and Descending orders.
Collects performance metrics (comparisons, swaps/shifts, runtime ms).
"""

import time
from dataclasses import dataclass
from typing import Any, Callable, List, Tuple


@dataclass
class SortResult:
    """Holds the sorted output and benchmarking metrics of a sort operation."""
    sorted_items: List[Any]
    comparisons: int
    swaps_or_shifts: int
    execution_time_ms: float
    algorithm: str
    criterion: str
    reverse: bool


def get_key_extractor(criterion: str) -> Callable[[Any], Any]:
    """Helper to obtain value extractor function based on sorting criterion."""
    crit = criterion.strip().lower()
    if crit in ("marks", "percentage", "total_marks", "score"):
        return lambda s: s.percentage
    elif crit in ("name", "student_name"):
        return lambda s: s.name.lower()
    elif crit in ("id", "student_id"):
        return lambda s: str(s.student_id).lower()
    else:
        return lambda s: s.student_id


def bubble_sort(
    arr: List[Any],
    criterion: str = "marks",
    reverse: bool = True,
) -> SortResult:
    """
    Bubble Sort Implementation.
    Repeatedly steps through the list, compares adjacent elements and swaps them
    if they are in the wrong order. Features an optimized early-exit flag.

    Time Complexity:
      - Best: O(n) [already sorted list]
      - Worst / Average: O(n^2)
    Space Complexity: O(1) auxiliary (in-place on shallow copy)
    """
    items = list(arr)
    n = len(items)
    key_func = get_key_extractor(criterion)
    comparisons = 0
    swaps = 0

    start_time = time.perf_counter()

    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            comparisons += 1
            val_a = key_func(items[j])
            val_b = key_func(items[j + 1])

            # Determine whether swap is needed
            should_swap = (val_a < val_b) if reverse else (val_a > val_b)
            if should_swap:
                items[j], items[j + 1] = items[j + 1], items[j]
                swaps += 1
                swapped = True

        if not swapped:
            break

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    return SortResult(
        sorted_items=items,
        comparisons=comparisons,
        swaps_or_shifts=swaps,
        execution_time_ms=elapsed_ms,
        algorithm="Bubble Sort",
        criterion=criterion,
        reverse=reverse,
    )


def insertion_sort(
    arr: List[Any],
    criterion: str = "marks",
    reverse: bool = True,
) -> SortResult:
    """
    Insertion Sort Implementation.
    Builds the sorted array one element at a time by shifting larger (or smaller)
    elements to the right.

    Time Complexity:
      - Best: O(n) [already sorted]
      - Worst / Average: O(n^2)
    Space Complexity: O(1) auxiliary
    """
    items = list(arr)
    n = len(items)
    key_func = get_key_extractor(criterion)
    comparisons = 0
    shifts = 0

    start_time = time.perf_counter()

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

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    return SortResult(
        sorted_items=items,
        comparisons=comparisons,
        swaps_or_shifts=shifts,
        execution_time_ms=elapsed_ms,
        algorithm="Insertion Sort",
        criterion=criterion,
        reverse=reverse,
    )


def merge_sort(
    arr: List[Any],
    criterion: str = "marks",
    reverse: bool = True,
) -> SortResult:
    """
    Merge Sort Implementation (Divide and Conquer).
    Recursively divides array into halves, sorts each half, and merges them.

    Time Complexity:
      - Best / Average / Worst: O(n log n)
    Space Complexity: O(n) auxiliary
    """
    items = list(arr)
    key_func = get_key_extractor(criterion)
    comparisons = 0
    moves = 0

    start_time = time.perf_counter()

    def _merge_sort_recursive(sub_arr: List[Any]) -> List[Any]:
        nonlocal comparisons, moves
        if len(sub_arr) <= 1:
            return sub_arr

        mid = len(sub_arr) // 2
        left_sorted = _merge_sort_recursive(sub_arr[:mid])
        right_sorted = _merge_sort_recursive(sub_arr[mid:])

        merged = []
        i = j = 0

        while i < len(left_sorted) and j < len(right_sorted):
            comparisons += 1
            val_l = key_func(left_sorted[i])
            val_r = key_func(right_sorted[j])

            condition = (val_l >= val_r) if reverse else (val_l <= val_r)
            if condition:
                merged.append(left_sorted[i])
                i += 1
            else:
                merged.append(right_sorted[j])
                j += 1
            moves += 1

        while i < len(left_sorted):
            merged.append(left_sorted[i])
            i += 1
            moves += 1

        while j < len(right_sorted):
            merged.append(right_sorted[j])
            j += 1
            moves += 1

        return merged

    sorted_result = _merge_sort_recursive(items)
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    return SortResult(
        sorted_items=sorted_result,
        comparisons=comparisons,
        swaps_or_shifts=moves,
        execution_time_ms=elapsed_ms,
        algorithm="Merge Sort",
        criterion=criterion,
        reverse=reverse,
    )
