"""
Searching Algorithms Implementation (CO2 & CO3).
Includes:
1. Linear Search: Sequential scan O(n).
2. Binary Search: Divide-and-conquer on sorted arrays O(log n).

Includes precise execution timing and comparison tracking for performance evaluation.
"""

import time
from dataclasses import dataclass
from typing import Any, Callable, List, Optional


@dataclass
class SearchResult:
    """Encapsulates the outcome of a search operation with performance metrics."""
    found: bool
    data: Optional[Any]
    index: int
    comparisons: int
    execution_time_ms: float
    algorithm: str


def linear_search(
    arr: List[Any],
    target: Any,
    key_func: Callable[[Any], Any] = lambda x: x,
) -> SearchResult:
    """
    Executes linear sequential search over an iterable.
    Time Complexity:
      - Best Case: O(1) [target at index 0]
      - Worst Case: O(n) [target at end or absent]
      - Average Case: O(n)
    Space Complexity: O(1) auxiliary
    """
    start = time.perf_counter()
    comparisons = 0
    found_item = None
    found_idx = -1

    target_str = str(target).strip().lower()

    for idx, item in enumerate(arr):
        comparisons += 1
        item_val = str(key_func(item)).strip().lower()
        if item_val == target_str:
            found_item = item
            found_idx = idx
            break

    elapsed_ms = (time.perf_counter() - start) * 1000.0

    return SearchResult(
        found=found_item is not None,
        data=found_item,
        index=found_idx,
        comparisons=comparisons,
        execution_time_ms=elapsed_ms,
        algorithm="Linear Search",
    )


def binary_search(
    sorted_arr: List[Any],
    target: Any,
    key_func: Callable[[Any], Any] = lambda x: x,
) -> SearchResult:
    """
    Executes binary search on a sorted contiguous sequence.
    Relies on O(1) random-access indexing to middle element.

    Time Complexity:
      - Best Case: O(1) [target at midpoint]
      - Worst Case: O(log n)
      - Average Case: O(log n)
    Space Complexity: O(1) auxiliary
    """
    start = time.perf_counter()
    low = 0
    high = len(sorted_arr) - 1
    comparisons = 0
    found_item = None
    found_idx = -1

    target_str = str(target).strip().lower()

    while low <= high:
        mid = (low + high) // 2
        comparisons += 1
        mid_val = str(key_func(sorted_arr[mid])).strip().lower()

        if mid_val == target_str:
            found_item = sorted_arr[mid]
            found_idx = mid
            break
        elif mid_val < target_str:
            low = mid + 1
        else:
            high = mid - 1

    elapsed_ms = (time.perf_counter() - start) * 1000.0

    return SearchResult(
        found=found_item is not None,
        data=found_item,
        index=found_idx,
        comparisons=comparisons,
        execution_time_ms=elapsed_ms,
        algorithm="Binary Search",
    )
