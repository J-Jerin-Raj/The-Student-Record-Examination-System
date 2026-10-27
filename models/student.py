"""
Student Model representing individual student academic records.
Provides helper properties for marks aggregation, percentage, and grading.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class Student:
    """Represents a student record with personal details and course marks."""
    student_id: str
    name: str
    department: str
    semester: int
    marks: Dict[str, float] = field(default_factory=dict)

    @property
    def total_marks(self) -> float:
        """Calculate total marks earned across all enrolled subjects."""
        if not self.marks:
            return 0.0
        return round(sum(self.marks.values()), 2)

    @property
    def max_possible_marks(self) -> float:
        """Calculate maximum possible marks assuming 100 per subject."""
        return len(self.marks) * 100.0 if self.marks else 100.0

    @property
    def percentage(self) -> float:
        """Calculate overall percentage score."""
        if not self.marks:
            return 0.0
        return round((self.total_marks / self.max_possible_marks) * 100.0, 2)

    @property
    def grade(self) -> str:
        """Determine letter grade based on overall percentage."""
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

    def copy(self) -> "Student":
        """Return a deep copy of the student object for undo stack preservation."""
        return Student(
            student_id=self.student_id,
            name=self.name,
            department=self.department,
            semester=self.semester,
            marks=dict(self.marks),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert student object to a serializable dictionary."""
        return {
            "student_id": self.student_id,
            "name": self.name,
            "department": self.department,
            "semester": self.semester,
            "marks": dict(self.marks),
            "total_marks": self.total_marks,
            "percentage": self.percentage,
            "grade": self.grade,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Student":
        """Instantiate a Student object from a dictionary."""
        return cls(
            student_id=str(data["student_id"]),
            name=str(data["name"]),
            department=str(data.get("department", "CSE")),
            semester=int(data.get("semester", 3)),
            marks={k: float(v) for k, v in data.get("marks", {}).items()},
        )

    def __repr__(self) -> str:
        return f"Student({self.student_id}, {self.name}, {self.percentage}%)"
