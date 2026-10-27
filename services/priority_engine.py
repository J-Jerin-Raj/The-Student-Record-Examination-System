"""
Priority Engine for Acadence.
Implements a transparent, rule-based scheduling and prioritization algorithm.
Explains exactly WHY a task is prioritized without opaque or fake AI claims.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from models import Task


@dataclass
class PriorityBreakdown:
    """Detailed score breakdown explaining task ranking."""
    urgency_score: float
    priority_score: float
    subject_vulnerability_score: float
    effort_score: float
    total_score: float
    is_overdue: bool
    hours_remaining: float
    rationale: str


class PriorityEngine:
    """
    Computes priority rankings using deterministic, rule-based academic factors:
    1. Urgency: Time remaining until deadline (hours).
    2. Explicit Priority: User-assigned level (Critical=40, High=30, Medium=20, Low=10).
    3. Subject Vulnerability: Penalty boost if student is struggling in this subject.
    4. Effort Feasibility: Quick-win vs heavy task balancing.
    """

    PRIORITY_WEIGHTS = {
        "Critical": 40.0,
        "High": 30.0,
        "Medium": 20.0,
        "Low": 10.0,
    }

    @classmethod
    def evaluate_task(
        cls,
        task: Task,
        subject_averages: Optional[Dict[str, float]] = None,
        warning_threshold: float = 60.0,
        reference_time: Optional[datetime] = None,
    ) -> PriorityBreakdown:
        if reference_time is None:
            reference_time = datetime.now()

        # 1. Parse Deadline and Calculate Urgency
        hours_remaining = 0.0
        is_overdue = False
        urgency_score = 0.0

        try:
            # Supports formats: YYYY-MM-DDTHH:MM or YYYY-MM-DD HH:MM or YYYY-MM-DD
            d_str = task.deadline.replace("T", " ")
            if len(d_str) == 10:
                d_str += " 23:59"
            deadline_dt = datetime.strptime(d_str[:16], "%Y-%m-%d %H:%M")
            delta = deadline_dt - reference_time
            hours_remaining = delta.total_seconds() / 3600.0

            if hours_remaining < 0:
                is_overdue = True
                # Overdue tasks receive a baseline of 100 plus 2 points per overdue day
                overdue_days = abs(hours_remaining) / 24.0
                urgency_score = 100.0 + min(50.0, overdue_days * 3.0)
            elif hours_remaining <= 24:
                # Due within 24 hours
                urgency_score = 90.0 - (hours_remaining / 24.0) * 15.0
            elif hours_remaining <= 48:
                # Due within 48 hours
                urgency_score = 75.0 - ((hours_remaining - 24.0) / 24.0) * 15.0
            elif hours_remaining <= 168:  # 7 days
                urgency_score = 60.0 - ((hours_remaining - 48.0) / 120.0) * 25.0
            else:
                # Due beyond 7 days
                urgency_score = max(5.0, 35.0 - (hours_remaining / 168.0) * 5.0)
        except Exception:
            urgency_score = 30.0
            hours_remaining = 72.0

        # 2. Priority Weight
        p_weight = cls.PRIORITY_WEIGHTS.get(task.priority, 20.0)

        # 3. Subject Vulnerability
        # If student's average in this subject is below threshold, prioritize to avoid failure
        vuln_score = 0.0
        subj_avg = None
        if subject_averages and task.subject in subject_averages:
            subj_avg = subject_averages[task.subject]
            if subj_avg < warning_threshold:
                gap = warning_threshold - subj_avg
                vuln_score = min(35.0, 15.0 + gap * 1.0)

        # 4. Effort Feasibility Factor
        # Tasks requiring 1-3 hours provide high return per study block
        effort = max(0.5, task.estimated_effort)
        if effort <= 3.0:
            effort_score = 15.0  # Quick win
        elif effort <= 6.0:
            effort_score = 10.0  # Moderate block
        else:
            effort_score = 5.0   # Large multi-session commitment

        # Total Composite Score
        total_score = round(urgency_score + p_weight + vuln_score + effort_score, 1)

        # Construct Transparent Rationale
        reasons = []
        if is_overdue:
            reasons.append(f"Overdue by {abs(hours_remaining):.1f} hours")
        elif hours_remaining <= 24:
            reasons.append(f"Urgent: Due in {hours_remaining:.1f} hours")
        elif hours_remaining <= 48:
            reasons.append(f"Due soon (within 2 days)")

        if p_weight >= 30.0:
            reasons.append(f"Marked as {task.priority} priority")

        if vuln_score > 0 and subj_avg is not None:
            reasons.append(f"Subject '{task.subject}' average is vulnerable ({subj_avg:.1f}%)")

        if effort <= 3.0:
            reasons.append(f"Quick win ({effort:.1f}h estimated)")

        rationale_text = " | ".join(reasons) if reasons else "Standard scheduled task"

        return PriorityBreakdown(
            urgency_score=round(urgency_score, 1),
            priority_score=round(p_weight, 1),
            subject_vulnerability_score=round(vuln_score, 1),
            effort_score=round(effort_score, 1),
            total_score=total_score,
            is_overdue=is_overdue,
            hours_remaining=round(hours_remaining, 1),
            rationale=rationale_text,
        )

    @classmethod
    def rank_tasks(
        cls,
        tasks: List[Task],
        subject_averages: Optional[Dict[str, float]] = None,
        warning_threshold: float = 60.0,
        include_completed: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Rank a collection of tasks using the Priority Engine scoring formula.
        Returns ranked list of dicts with task object, breakdown, and rank index.
        """
        filtered = [t for t in tasks if include_completed or t.status != "Completed"]
        evaluated = []

        for t in filtered:
            breakdown = cls.evaluate_task(t, subject_averages, warning_threshold)
            evaluated.append({
                "task": t,
                "breakdown": breakdown,
                "score": breakdown.total_score,
            })

        # Sort descending by composite priority score
        evaluated.sort(key=lambda x: x["score"], reverse=True)

        # Assign rank numbers
        for idx, item in enumerate(evaluated, start=1):
            item["rank"] = idx

        return evaluated
