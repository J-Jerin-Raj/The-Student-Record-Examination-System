"""
UndoAction Model for Acadence.
Represents an invertible action token stored in the LIFO Undo Stack.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class UndoAction:
    """Represents an invertible action token stored in the LIFO Undo Stack."""
    entity_type: str  # 'task', 'exam', 'assessment'
    action_type: str  # 'CREATE', 'UPDATE', 'DELETE', 'STATUS_CHANGE'
    entity_id: Optional[int] = None
    previous_state: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None
    description: str = ""
