"""
Custom Queue Data Structure Implementation (CO1).
Operates on the First-In, First-Out (FIFO) principle.
Implemented using linked nodes with front and rear pointers to guarantee
O(1) time complexity for both enqueue and dequeue operations without shifting overhead.
Used to manage examination requests (registration, hall-ticket generation, re-evaluation).
"""

from typing import Any, List, Optional
from structures.node import Node


class Queue:
    """
    A FIFO queue implemented with front and rear pointers.
    Guarantees strict O(1) enqueue and dequeue operations.
    """

    def __init__(self, capacity: Optional[int] = None):
        self._front: Optional[Node] = None
        self._rear: Optional[Node] = None
        self._count: int = 0
        self._capacity: Optional[int] = capacity

    def is_empty(self) -> bool:
        """Check if queue is empty. Time Complexity: O(1)"""
        return self._front is None

    def size(self) -> int:
        """Return number of elements in the queue. Time Complexity: O(1)"""
        return self._count

    def __len__(self) -> int:
        return self._count

    def enqueue(self, item: Any) -> None:
        """
        Add an element to the rear of the queue.
        Time Complexity: O(1)
        """
        if self._capacity is not None and self._count >= self._capacity:
            raise OverflowError("Queue overflow: Capacity limit reached.")

        new_node = Node(item)
        if self._rear is None:
            self._front = self._rear = new_node
        else:
            self._rear.next = new_node
            self._rear = new_node
        self._count += 1

    def dequeue(self) -> Any:
        """
        Remove and return the element at the front of the queue.
        Raises IndexError if the queue is empty.
        Time Complexity: O(1)
        """
        if self.is_empty():
            raise IndexError("Queue underflow: Cannot dequeue from an empty queue.")

        removed_data = self._front.data
        self._front = self._front.next
        if self._front is None:
            self._rear = None
        self._count -= 1
        return removed_data

    def peek(self) -> Optional[Any]:
        """
        Return the front element without removing it.
        Returns None if queue is empty.
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None
        return self._front.data

    def clear(self) -> None:
        """Empty the queue. Time Complexity: O(1)"""
        self._front = None
        self._rear = None
        self._count = 0

    def to_list(self) -> List[Any]:
        """
        Return all queue elements from front to rear as a Python list.
        Time Complexity: O(n)
        """
        items = []
        current = self._front
        while current is not None:
            items.append(current.data)
            current = current.next
        return items

    def __repr__(self) -> str:
        return f"Queue({self.to_list()})"
