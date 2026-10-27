"""
Academic Request Model for Acadence.
Represents a student academic service request managed in a FIFO Queue.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class AcademicRequest:
    """Represents a student academic service request managed in FIFO Queue."""
    id: Optional[int] = None
    request_id: str = ""
    student_name: str = "Student"
    request_type: str = "Re-evaluation"  # Hall Ticket, Re-evaluation, Doubt Session, Transcript
    subject: str = ""
    details: str = ""
    status: str = "Pending"  # Pending, Processed
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
