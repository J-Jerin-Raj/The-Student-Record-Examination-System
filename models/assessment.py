"""
Assessment Model for Acadence.
Represents a student assessment score (quiz, test, assignment, or final).
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class Assessment:
    """Represents a student assessment score (quiz, test, assignment, or final)."""
    id: Optional[int] = None
    subject: str = ""
    assessment_name: str = ""
    assessment_type: str = "Internal"  # Quiz, Assignment, Internal, Lab, Final
    max_marks: float = 100.0
    marks_obtained: float = 0.0
    weightage: float = 20.0  # Percentage weight
    assessment_date: str = ""  # YYYY-MM-DD
    notes: str = ""

    @property
    def percentage(self) -> float:
        if self.max_marks <= 0:
            return 0.0
        return round((self.marks_obtained / self.max_marks) * 100.0, 2)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["percentage"] = self.percentage
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Assessment":
        return cls(
            id=data.get("id"),
            subject=data.get("subject", ""),
            assessment_name=data.get("assessment_name", ""),
            assessment_type=data.get("assessment_type", "Internal"),
            max_marks=float(data.get("max_marks", 100.0)),
            marks_obtained=float(data.get("marks_obtained", 0.0)),
            weightage=float(data.get("weightage", 20.0)),
            assessment_date=data.get("assessment_date", datetime.now().strftime("%Y-%m-%d")),
            notes=data.get("notes", ""),
        )
