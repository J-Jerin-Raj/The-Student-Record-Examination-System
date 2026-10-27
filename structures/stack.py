"""
Custom Stack Data Structure Implementation (CO1).
Operates on the Last-In, First-Out (LIFO) principle.
Used in this project to implement an Undo engine for student record modifications.
"""

from typing import Any, List, Optional


class Stack:
    """
    A LIFO stack implemented with dynamic internal storage.
    Supports push, pop, peek, size, and emptiness check in O(1) time complexity.
    """

    def __init__(self, capacity: Optional[int] = None):
        self._items: List[Any] = []
        self._capacity: Optional[int] = capacity

    def push(self, item: Any) -> None:
        """
        Push an item onto the top of the stack.
        Time Complexity: O(1)
        """
        if self._capacity is not None and len(self._items) >= self._capacity:
            raise OverflowError("Stack overflow: Maximum capacity reached.")
        self._items.append(item)

    def pop(self) -> Any:
        """
        Remove and return the top item from the stack.
        Raises IndexError if the stack is empty.
        Time Complexity: O(1)
        """
        if self.is_empty():
            raise IndexError("Stack underflow: Cannot pop from an empty stack.")
        return self._items.pop()

    def peek(self) -> Optional[Any]:
        """
        Return the top item without removing it.
        Returns None if stack is empty.
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None
        return self._items[-1]

    def is_empty(self) -> bool:
        """Check if the stack contains no elements. Time Complexity: O(1)"""
        return len(self._items) == 0

    def size(self) -> int:
        """Return the current number of elements in the stack. Time Complexity: O(1)"""
        return len(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def clear(self) -> None:
        """Reset the stack. Time Complexity: O(1)"""
        self._items.clear()

    def to_list(self) -> List[Any]:
        """Return a copy of items from bottom to top."""
        return list(self._items)

    def __repr__(self) -> str:
        return f"Stack({self._items})"
