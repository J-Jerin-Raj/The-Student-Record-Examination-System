"""
Student Profile Model for Acadence.
Represents student academic profile details and grade computations.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Student:
    """Represents student academic profile details."""
    student_id: str = "STU101"
    name: str = "Alex Chen"
    department: str = "Computer Science & Engineering"
    semester: int = 3
    marks: Dict[str, float] = field(default_factory=dict)

    @property
    def percentage(self) -> float:
        if not self.marks:
            return 0.0
        return round(sum(self.marks.values()) / (len(self.marks) * 100.0) * 100.0, 2)

    @property
    def grade(self) -> str:
        pct = self.percentage
        if pct >= 90:
            return "O (Outstanding)"
        elif pct >= 80:
            return "A+ (Excellent)"
        elif pct >= 70:
            return "A (Very Good)"
        elif pct >= 60:
            return "B+ (Good)"
        elif pct >= 50:
            return "B (Above Average)"
        elif pct >= 40:
            return "C (Pass)"
        else:
            return "F (Fail)"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "student_id": self.student_id,
            "name": self.name,
            "department": self.department,
            "semester": self.semester,
            "marks": self.marks,
            "percentage": self.percentage,
            "grade": self.grade,
        }
