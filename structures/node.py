"""
Custom Node class for Singly Linked List implementation.
Each node holds a data reference and a reference to the next node.
"""

from typing import Any, Optional


class Node:
    """Represents an individual node in a singly linked list."""

    def __init__(self, data: Any, next_node: Optional["Node"] = None):
        self.data: Any = data
        self.next: Optional["Node"] = next_node

    def __repr__(self) -> str:
        return f"Node({self.data})"
