"""
Searching Algorithms Implementation (CO2 & CO3).
Includes:
1. Linear Search (Sequential scan on Linked List & Array/List)
2. Binary Search (Divide and conquer on sorted Array/List)

Technical Note:
Binary search demands random access O(1) to the middle element (arr[mid]).
In a singly linked list, accessing node 'mid' requires sequential traversal from head (O(mid)),
which degrades binary search to O(n) or O(n log n). Hence, binary search is executed on
contiguous array-backed lists for optimal O(log n) performance.
"""

import time
from typing import Any, Callable, List, Optional, Tuple
from dataclasses import dataclass
from structures.linked_list import SinglyLinkedList


@dataclass
class SearchResult:
    """Encapsulates the outcome, comparison count, and runtime of a search operation."""
    found: bool
    data: Optional[Any]
    comparisons: int
    execution_time_ms: float
    data_structure: str
    algorithm: str


def linear_search_linked_list(
    ll: SinglyLinkedList,
    target_value: Any,
    key_func: Callable[[Any], Any] = lambda x: x.student_id,
) -> SearchResult:
    """
    Sequentially traverses each node in the custom SinglyLinkedList.
    Time Complexity:
      - Best: O(1) [target at head]
      - Worst: O(n) [target at tail or not found]
      - Average: O(n)
    Space Complexity: O(1)
    """
    start_time = time.perf_counter()
    current = ll.head
    comparisons = 0
    found_data = None

    while current is not None:
        comparisons += 1
        val = key_func(current.data)
        if str(val).strip().lower() == str(target_value).strip().lower():
            found_data = current.data
            break
        current = current.next

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    return SearchResult(
        found=found_data is not None,
        data=found_data,
        comparisons=comparisons,
        execution_time_ms=elapsed_ms,
        data_structure="Singly Linked List",
        algorithm="Linear Search",
    )


def linear_search_list(
    arr: List[Any],
    target_value: Any,
    key_func: Callable[[Any], Any] = lambda x: x.student_id,
) -> SearchResult:
    """
    Sequentially scans a Python list (array).
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    start_time = time.perf_counter()
    comparisons = 0
    found_data = None

    for item in arr:
        comparisons += 1
        val = key_func(item)
        if str(val).strip().lower() == str(target_value).strip().lower():
            found_data = item
            break

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    return SearchResult(
        found=found_data is not None,
        data=found_data,
        comparisons=comparisons,
        execution_time_ms=elapsed_ms,
        data_structure="Python List (Array)",
        algorithm="Linear Search",
    )


def binary_search(
    sorted_arr: List[Any],
    target_value: Any,
    key_func: Callable[[Any], Any] = lambda x: x.student_id,
) -> SearchResult:
    """
    Executes binary search on a pre-sorted list using divide-and-conquer.
    Relies on O(1) random-access indexing to mid.
    Time Complexity:
      - Best: O(1) [target at middle]
      - Worst: O(log n)
      - Average: O(log n)
    Space Complexity: O(1)
    """
    start_time = time.perf_counter()
    low = 0
    high = len(sorted_arr) - 1
    comparisons = 0
    found_data = None

    target_str = str(target_value).strip().lower()

    while low <= high:
        mid = (low + high) // 2
        comparisons += 1
        mid_val = str(key_func(sorted_arr[mid])).strip().lower()

        if mid_val == target_str:
            found_data = sorted_arr[mid]
            break
        elif mid_val < target_str:
            low = mid + 1
        else:
            high = mid - 1

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    return SearchResult(
        found=found_data is not None,
        data=found_data,
        comparisons=comparisons,
        execution_time_ms=elapsed_ms,
        data_structure="Python List (Array with O(1) indexing)",
        algorithm="Binary Search",
    )
