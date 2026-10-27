"""
Exam Model for Acadence.
Represents an upcoming or scheduled examination.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class Exam:
    """Represents an upcoming or scheduled examination."""
    id: Optional[int] = None
    subject: str = ""
    exam_date: str = ""  # YYYY-MM-DD
    start_time: str = "09:30"  # HH:MM
    end_time: str = "12:30"  # HH:MM
    venue: str = "Hall A"
    syllabus: str = ""
    revision_progress: float = 0.0  # 0 to 100%
    priority: str = "High"  # Critical, High, Medium, Low
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Exam":
        return cls(
            id=data.get("id"),
            subject=data.get("subject", ""),
            exam_date=data.get("exam_date", ""),
            start_time=data.get("start_time", "09:30"),
            end_time=data.get("end_time", "12:30"),
            venue=data.get("venue", "Hall A"),
            syllabus=data.get("syllabus", ""),
            revision_progress=float(data.get("revision_progress", 0.0)),
            priority=data.get("priority", "High"),
            created_at=data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
