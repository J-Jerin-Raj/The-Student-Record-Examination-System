"""
Academic Rescue Mode Service.
Flagship problem-solving engine in Acadence.
Activated when students face overlapping exams, overdue deadlines, and lagging grades.
Aggregates vulnerable subjects, urgent tasks, and computes transparent Rescue Recommendations.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from models import Task
import database as db
from services.priority_engine import PriorityEngine
from services.performance_analyzer import PerformanceAnalyzerService


class AcademicRescueService:
    """Calculates Academic Rescue triage recommendations and action plans."""

    @classmethod
    def analyze_rescue_state(cls, warning_threshold: float = 60.0) -> Dict[str, Any]:
        """
        Gathers academic risk factors across tasks, exams, and marks:
        1. Overdue and impending tasks (< 7 days).
        2. Subjects performing below the warning threshold.
        3. Imminent exams within 10 days.
        4. Prioritizes the top recommended tasks with plain-language explanations.
        """
        all_tasks = db.get_all_tasks()
        all_exams = db.get_all_exams()
        now = datetime.now()

        # Subject performance map
        perf_data = PerformanceAnalyzerService.get_subject_summaries(warning_threshold)
        subject_averages = {s: data["average_percentage"] for s, data in perf_data["subjects"].items()}
        vulnerable_subjects = [s for s, data in perf_data["subjects"].items() if data["status"] in ("Critical", "Vulnerable")]

        # Imminent exams (< 10 days)
        imminent_exams = []
        for e in all_exams:
            try:
                edt = datetime.strptime(e.exam_date, "%Y-%m-%d")
                delta_days = (edt - now).days
                if 0 <= delta_days <= 10:
                    imminent_exams.append({
                        "exam": e.to_dict(),
                        "days_remaining": delta_days,
                    })
            except Exception:
                pass

        # Filter active tasks
        active_tasks = [t for t in all_tasks if t.status != "Completed"]

        # Evaluate using PriorityEngine
        evaluated_tasks = []
        overdue_count = 0
        due_soon_count = 0

        for t in active_tasks:
            breakdown = PriorityEngine.evaluate_task(t, subject_averages, warning_threshold, now)
            if breakdown.is_overdue:
                overdue_count += 1
            elif breakdown.hours_remaining <= 48:
                due_soon_count += 1

            # Composite Rescue Score
            # Heavy weighting on urgency (0.45), vulnerability (0.30), priority (0.15), effort (0.10)
            rescue_score = (
                breakdown.urgency_score * 0.45 +
                breakdown.subject_vulnerability_score * 0.35 +
                breakdown.priority_score * 0.15 +
                breakdown.effort_score * 0.05
            )

            # Generate rescue advice
            rescue_rationale = []
            if breakdown.is_overdue:
                rescue_rationale.append("Overdue: High penalty risk")
            elif breakdown.hours_remaining <= 24:
                rescue_rationale.append("Imminent deadline (< 24h)")
            elif breakdown.hours_remaining <= 48:
                rescue_rationale.append("Approaching deadline (< 48h)")

            if t.subject in vulnerable_subjects:
                avg = subject_averages.get(t.subject, 0.0)
                rescue_rationale.append(f"Subject '{t.subject}' is below threshold ({avg:.1f}%)")

            if any(e["exam"]["subject"] == t.subject for e in imminent_exams):
                rescue_rationale.append(f"Upcoming exam in {t.subject} in < 10 days")

            if t.estimated_effort <= 2.5:
                rescue_rationale.append(f"High ROI quick-win ({t.estimated_effort}h effort)")

            evaluated_tasks.append({
                "task": t.to_dict(),
                "rescue_score": round(rescue_score, 1),
                "breakdown": {
                    "urgency": breakdown.urgency_score,
                    "vulnerability": breakdown.subject_vulnerability_score,
                    "priority": breakdown.priority_score,
                    "effort": breakdown.effort_score,
                    "is_overdue": breakdown.is_overdue,
                    "hours_remaining": breakdown.hours_remaining,
                },
                "rationale": " • ".join(rescue_rationale) if rescue_rationale else "Scheduled academic requirement",
            })

        # Sort descending by Rescue Score
        evaluated_tasks.sort(key=lambda x: x["rescue_score"], reverse=True)

        # Top 4 recommendations for immediate focus
        top_recommendations = evaluated_tasks[:4]

        # Calculate overall academic stress / crisis index (0 to 100)
        crisis_score = 0.0
        if overdue_count > 0:
            crisis_score += min(40.0, overdue_count * 15.0)
        if len(vulnerable_subjects) > 0:
            crisis_score += min(35.0, len(vulnerable_subjects) * 12.0)
        if len(imminent_exams) > 0:
            crisis_score += min(25.0, len(imminent_exams) * 8.0)
        crisis_score = min(100.0, round(crisis_score, 1))

        if crisis_score >= 70:
            status_level = "Severe Academic Pressure"
            action_statement = "Take immediate action: Complete overdue items first and focus strictly on top recommendations."
        elif crisis_score >= 40:
            status_level = "Moderate Workload Warning"
            action_statement = "Prioritize tasks due in the next 48 hours and reinforce vulnerable subjects."
        else:
            status_level = "Stable Academic Standing"
            action_statement = "Workload is manageable. Maintain your scheduled pace to stay ahead."

        return {
            "crisis_index": crisis_score,
            "status_level": status_level,
            "action_statement": action_statement,
            "overdue_tasks_count": overdue_count,
            "due_soon_count": due_soon_count,
            "vulnerable_subjects": vulnerable_subjects,
            "imminent_exams_count": len(imminent_exams),
            "top_recommendations": top_recommendations,
            "total_rescue_candidates": len(evaluated_tasks),
        }
