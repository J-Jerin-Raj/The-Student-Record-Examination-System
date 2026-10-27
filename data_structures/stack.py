"""
Custom LIFO Stack Implementation (CO1).
Provides constant-time push, pop, peek, and status queries.
Used across Acadence to power the Multi-Level Undo Engine for tasks, exams, and grades.
"""

from typing import Any, List, Optional


class Stack:
    """A Last-In, First-Out (LIFO) stack data structure."""

    def __init__(self, capacity: Optional[int] = 100):
        self._items: List[Any] = []
        self._capacity: Optional[int] = capacity

    def push(self, item: Any) -> None:
        """
        Push an item onto the top of the stack.
        Time Complexity: O(1)
        """
        if self._capacity is not None and len(self._items) >= self._capacity:
            # Drop the oldest item if bounded capacity exceeded to prevent unbounded memory growth
            self._items.pop(0)
        self._items.append(item)

    def pop(self) -> Any:
        """
        Remove and return the most recently pushed item.
        Raises IndexError if the stack is empty.
        Time Complexity: O(1)
        """
        if self.is_empty():
            raise IndexError("Stack underflow: Cannot pop from an empty stack.")
        return self._items.pop()

    def peek(self) -> Optional[Any]:
        """
        Return the top item without removing it.
        Returns None if the stack is empty.
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None
        return self._items[-1]

    def is_empty(self) -> bool:
        """Check if stack is empty. Time Complexity: O(1)"""
        return len(self._items) == 0

    def size(self) -> int:
        """Return the count of elements in the stack. Time Complexity: O(1)"""
        return len(self._items)

    def clear(self) -> None:
        """Remove all elements from the stack. Time Complexity: O(1)"""
        self._items.clear()

    def to_list(self) -> List[Any]:
        """Return a shallow copy of items in bottom-to-top order."""
        return list(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __repr__(self) -> str:
        return f"Stack({self._items})"
