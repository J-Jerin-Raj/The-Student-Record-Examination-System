"""
Custom Singly Linked List Implementation (CO2).
Demonstrates dynamic node allocation, pointer chaining, and linear traversal.

DSA Evaluation Note:
A singly linked list is optimal for frequent insertions and deletions at the head O(1),
avoiding the O(n) contiguous array element shifting incurred by standard lists.
However, searching and indexing require O(n) sequential pointer chasing because
elements are not stored contiguously in memory.
"""

from typing import Any, Callable, Generator, List, Optional, Tuple
from data_structures.node import Node


class SinglyLinkedList:
    """
    A custom singly linked list holding academic records (tasks or exams).
    Supports insertion, deletion, updating, traversal, and linear search.
    """

    def __init__(self):
        self.head: Optional[Node] = None
        self._size: int = 0

    def is_empty(self) -> bool:
        """Check if linked list contains zero nodes. Time: O(1)"""
        return self.head is None

    def __len__(self) -> int:
        """Return the count of nodes. Time: O(1)"""
        return self._size

    def insert_front(self, data: Any) -> None:
        """
        Insert a new node at the beginning (head) of the list.
        Time Complexity: O(1)
        """
        new_node = Node(data, next_node=self.head)
        self.head = new_node
        self._size += 1

    def insert_rear(self, data: Any) -> None:
        """
        Insert a new node at the end (tail) of the list.
        Time Complexity: O(n)
        """
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
        else:
            curr = self.head
            while curr.next is not None:
                curr = curr.next
            curr.next = new_node
        self._size += 1

    def _extract_id(self, item: Any) -> str:
        """Extract identifier string from either an object, dict, or primitive."""
        if hasattr(item, "id"):
            return str(getattr(item, "id"))
        elif isinstance(item, dict) and "id" in item:
            return str(item["id"])
        elif hasattr(item, "task_id"):
            return str(getattr(item, "task_id"))
        elif hasattr(item, "exam_id"):
            return str(getattr(item, "exam_id"))
        return str(item)

    def delete_by_id(self, target_id: str) -> Tuple[Optional[Any], int]:
        """
        Delete node whose data matches target_id.
        Returns tuple of (deleted_data_or_None, comparisons_count).
        Time Complexity: O(n)
        """
        if self.head is None:
            return None, 0

        target_str = str(target_id)
        comparisons = 0
        curr = self.head
        prev: Optional[Node] = None

        while curr is not None:
            comparisons += 1
            if self._extract_id(curr.data) == target_str:
                if prev is None:
                    self.head = curr.next
                else:
                    prev.next = curr.next
                self._size -= 1
                return curr.data, comparisons
            prev = curr
            curr = curr.next

        return None, comparisons

    def update_by_id(self, target_id: str, new_data: Any) -> Tuple[bool, Optional[Any]]:
        """
        Update the data payload of the node matching target_id.
        Returns (success_flag, previous_data_snapshot).
        Time Complexity: O(n)
        """
        target_str = str(target_id)
        curr = self.head
        while curr is not None:
            if self._extract_id(curr.data) == target_str:
                old_data = curr.data
                curr.data = new_data
                return True, old_data
            curr = curr.next
        return False, None

    def search_by_id(self, target_id: str) -> Tuple[Optional[Any], int]:
        """
        Linear search traversal through nodes comparing target_id.
        Returns (found_data_or_None, comparisons_count).
        Time Complexity: O(n)
        """
        target_str = str(target_id)
        comparisons = 0
        curr = self.head
        while curr is not None:
            comparisons += 1
            if self._extract_id(curr.data) == target_str:
                return curr.data, comparisons
            curr = curr.next
        return None, comparisons

    def to_list(self) -> List[Any]:
        """
        Traverse the list and return elements as a Python list.
        Time Complexity: O(n)
        """
        items = []
        curr = self.head
        while curr is not None:
            items.append(curr.data)
            curr = curr.next
        return items

    def clear(self) -> None:
        """Clear the linked list. Time Complexity: O(1)"""
        self.head = None
        self._size = 0

    def __iter__(self) -> Generator[Any, None, None]:
        curr = self.head
        while curr is not None:
            yield curr.data
            curr = curr.next

    def __repr__(self) -> str:
        return f"SinglyLinkedList({self.to_list()})"
