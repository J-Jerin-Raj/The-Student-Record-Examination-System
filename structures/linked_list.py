"""
Custom Singly Linked List Implementation for Student Records Storage (CO2).
Demonstrates dynamic node allocation, pointer manipulation, sequential traversal,
insertion, deletion, updating, and search.
"""

from typing import Any, Callable, Generator, List, Optional, Tuple
from structures.node import Node


class SinglyLinkedList:
    """
    A custom singly linked list supporting CRUD operations and sequential traversal.
    Maintains a head pointer and tracking count for O(1) size queries.
    """

    def __init__(self):
        self.head: Optional[Node] = None
        self._count: int = 0

    def is_empty(self) -> bool:
        """Check if the linked list has no elements. Time Complexity: O(1)"""
        return self.head is None

    def __len__(self) -> int:
        """Return the number of elements in the linked list. Time Complexity: O(1)"""
        return self._count

    def insert_at_beginning(self, data: Any) -> None:
        """
        Insert a new node at the front (head) of the list.
        Time Complexity: O(1)
        """
        new_node = Node(data, next_node=self.head)
        self.head = new_node
        self._count += 1

    def insert_at_end(self, data: Any) -> None:
        """
        Insert a new node at the end (tail) of the list.
        Time Complexity: O(n)
        """
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.next is not None:
                current = current.next
            current.next = new_node
        self._count += 1

    def delete_by_id(self, student_id: str) -> Tuple[Optional[Any], int]:
        """
        Delete a student node matching the given student_id.
        Returns a tuple: (deleted_student_object_or_None, comparison_count).
        Time Complexity: O(n)
        """
        if self.head is None:
            return None, 0

        comparisons = 0
        current = self.head
        prev: Optional[Node] = None

        while current is not None:
            comparisons += 1
            # Assuming student object has student_id attribute or dict key
            current_id = getattr(current.data, "student_id", None)
            if current_id is None and isinstance(current.data, dict):
                current_id = current.data.get("student_id")

            if current_id == student_id:
                if prev is None:
                    # Deleting head node
                    self.head = current.next
                else:
                    prev.next = current.next
                self._count -= 1
                return current.data, comparisons

            prev = current
            current = current.next

        return None, comparisons

    def update_by_id(self, student_id: str, new_data: Any) -> Tuple[bool, Optional[Any]]:
        """
        Update the data of a node matching student_id.
        Returns (success_boolean, old_data_for_undo).
        Time Complexity: O(n)
        """
        current = self.head
        while current is not None:
            curr_id = getattr(current.data, "student_id", None)
            if curr_id is None and isinstance(current.data, dict):
                curr_id = current.data.get("student_id")

            if curr_id == student_id:
                old_data = current.data
                current.data = new_data
                return True, old_data
            current = current.next
        return False, None

    def search_by_id(self, student_id: str) -> Tuple[Optional[Any], int]:
        """
        Linear search by student_id in the linked list.
        Returns (student_or_None, comparison_count).
        Time Complexity: O(n)
        """
        comparisons = 0
        current = self.head
        while current is not None:
            comparisons += 1
            curr_id = getattr(current.data, "student_id", None)
            if curr_id is None and isinstance(current.data, dict):
                curr_id = current.data.get("student_id")

            if curr_id == student_id:
                return current.data, comparisons
            current = current.next

        return None, comparisons

    def search_by_predicate(self, predicate: Callable[[Any], bool]) -> List[Any]:
        """
        Search and collect all items matching a predicate function.
        Time Complexity: O(n)
        """
        matches = []
        current = self.head
        while current is not None:
            if predicate(current.data):
                matches.append(current.data)
            current = current.next
        return matches

    def to_list(self) -> List[Any]:
        """
        Convert linked list items to a standard Python list.
        Time Complexity: O(n)
        """
        items = []
        current = self.head
        while current is not None:
            items.append(current.data)
            current = current.next
        return items

    def clear(self) -> None:
        """Empty the linked list. Time Complexity: O(1)"""
        self.head = None
        self._count = 0

    def __iter__(self) -> Generator[Any, None, None]:
        """Allow iteration over elements: for student in linked_list: ..."""
        current = self.head
        while current is not None:
            yield current.data
            current = current.next
