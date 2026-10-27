"""
Custom Node implementation for linked structures.
Holds data and reference to the next node.
"""

from typing import Any, Optional


class Node:
    """A node in a singly linked list or linked queue."""

    def __init__(self, data: Any, next_node: Optional["Node"] = None):
        self.data: Any = data
        self.next: Optional["Node"] = next_node

    def __repr__(self) -> str:
        return f"Node({self.data})"
