"""
Custom FIFO Queue Implementation (CO1).
Built using dynamic linked nodes with front and rear pointers to guarantee
strict O(1) time complexity for enqueue and dequeue operations without array shifting.
Used in Acadence to manage student academic service requests and study session pipelines.
"""

from typing import Any, List, Optional
from data_structures.node import Node


class Queue:
    """A First-In, First-Out (FIFO) queue data structure."""

    def __init__(self, capacity: Optional[int] = None):
        self._front: Optional[Node] = None
        self._rear: Optional[Node] = None
        self._count: int = 0
        self._capacity: Optional[int] = capacity

    def is_empty(self) -> bool:
        """Check if queue has no elements. Time Complexity: O(1)"""
        return self._front is None

    def size(self) -> int:
        """Return the number of elements in the queue. Time Complexity: O(1)"""
        return self._count

    def enqueue(self, item: Any) -> None:
        """
        Add an item to the rear of the queue.
        Time Complexity: O(1)
        """
        if self._capacity is not None and self._count >= self._capacity:
            raise OverflowError("Queue overflow: Maximum capacity reached.")

        new_node = Node(item)
        if self._rear is None:
            self._front = self._rear = new_node
        else:
            self._rear.next = new_node
            self._rear = new_node
        self._count += 1

    def dequeue(self) -> Any:
        """
        Remove and return the item at the front of the queue.
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

    def front(self) -> Optional[Any]:
        """
        Return the front item without removing it.
        Returns None if queue is empty.
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None
        return self._front.data

    def peek(self) -> Optional[Any]:
        """Alias for front()."""
        return self.front()

    def clear(self) -> None:
        """Empty the queue. Time Complexity: O(1)"""
        self._front = None
        self._rear = None
        self._count = 0

    def to_list(self) -> List[Any]:
        """
        Return all items from front to rear as a standard Python list.
        Time Complexity: O(n)
        """
        items = []
        curr = self._front
        while curr is not None:
            items.append(curr.data)
            curr = curr.next
        return items

    def __len__(self) -> int:
        return self._count

    def __repr__(self) -> str:
        return f"Queue({self.to_list()})"
