"""
Academic Performance Analyzer Service.
Computes subject performance summaries, detects declining trends using explainable rules,
evaluates warning thresholds, and provides a reverse target score calculator.
"""

from typing import Any, Dict, List, Optional, Tuple
from models import Assessment, Exam
import database as db


class PerformanceAnalyzerService:
    """Evaluates student academic performance and computes actionable indicators."""

    @staticmethod
    def get_subject_summaries(warning_threshold: float = 60.0) -> Dict[str, Any]:
        """
        Calculates aggregate statistics, averages, and status for each subject.
        """
        assessments = db.get_all_assessments()
        by_subject: Dict[str, List[Assessment]] = {}

        for a in assessments:
            if a.subject not in by_subject:
                by_subject[a.subject] = []
            by_subject[a.subject].append(a)

        subject_stats = {}
        total_weighted_points = 0.0
        total_weights = 0.0

        for subject, a_list in by_subject.items():
            # Sort chronologically
            a_list.sort(key=lambda x: x.assessment_date)

            pct_list = [a.percentage for a in a_list]
            avg_pct = round(sum(pct_list) / len(pct_list), 2)

            for a in a_list:
                total_weighted_points += a.percentage * a.weightage
                total_weights += a.weightage

            # Decline detection rules
            is_declining = False
            decline_reason = ""
            if len(pct_list) >= 2:
                recent = pct_list[-1]
                prev = pct_list[-2]
                drop = prev - recent

                if drop >= 10.0:
                    is_declining = True
                    decline_reason = f"Recent drop of {drop:.1f}% ({prev}% to {recent}%)"
                elif len(pct_list) >= 3 and (pct_list[-3] > pct_list[-2] > pct_list[-1]):
                    is_declining = True
                    decline_reason = f"Consecutive downward trend over last 3 assessments"

            # Threshold check
            if avg_pct < 50.0:
                status = "Critical"
            elif avg_pct < warning_threshold:
                status = "Vulnerable"
            elif avg_pct < 80.0:
                status = "Proficient"
            else:
                status = "Exemplary"

            subject_stats[subject] = {
                "subject": subject,
                "assessment_count": len(a_list),
                "average_percentage": avg_pct,
                "highest_percentage": max(pct_list),
                "lowest_percentage": min(pct_list),
                "status": status,
                "is_declining": is_declining,
                "decline_reason": decline_reason,
                "assessments": [a.to_dict() for a in a_list],
            }

        overall_avg = round(total_weighted_points / max(1.0, total_weights), 2) if total_weights > 0 else 0.0

        return {
            "overall_average": overall_avg,
            "overall_grade": PerformanceAnalyzerService.get_letter_grade(overall_avg),
            "subjects": subject_stats,
            "total_assessments": len(assessments),
        }

    @staticmethod
    def get_letter_grade(pct: float) -> str:
        """Map percentage to academic letter grade."""
        if pct >= 90.0:
            return "O (Outstanding)"
        elif pct >= 80.0:
            return "A+ (Excellent)"
        elif pct >= 70.0:
            return "A (Very Good)"
        elif pct >= 60.0:
            return "B+ (Good)"
        elif pct >= 50.0:
            return "B (Above Average)"
        elif pct >= 40.0:
            return "C (Pass)"
        else:
            return "F (Fail)"

    @staticmethod
    def calculate_required_score(
        subject: str,
        target_average: float,
        upcoming_max_marks: float = 100.0,
        upcoming_weightage: float = 30.0,
    ) -> Dict[str, Any]:
        """
        Reverse calculates the score required on an upcoming assessment
        to achieve a targeted overall subject average.
        """
        assessments = [a for a in db.get_all_assessments() if a.subject == subject]
        if not assessments:
            # No existing marks, target average is directly the required percentage
            needed_marks = round((target_average / 100.0) * upcoming_max_marks, 1)
            return {
                "subject": subject,
                "current_average": 0.0,
                "target_average": target_average,
                "upcoming_max_marks": upcoming_max_marks,
                "required_marks": needed_marks,
                "required_percentage": target_average,
                "is_achievable": 0.0 <= target_average <= 100.0,
                "advice": f"Score at least {needed_marks}/{upcoming_max_marks} ({target_average}%) to hit your goal.",
            }

        total_weighted_pts = sum(a.percentage * a.weightage for a in assessments)
        existing_weight = sum(a.weightage for a in assessments)
        current_avg = round(total_weighted_pts / max(0.001, existing_weight), 2)

        # Formula: (total_weighted_pts + X_pct * upcoming_weight) / (existing_weight + upcoming_weight) = target_average
        new_total_weight = existing_weight + upcoming_weightage
        needed_weighted_pts = (target_average * new_total_weight) - total_weighted_pts
        required_pct = round(needed_weighted_pts / max(0.001, upcoming_weightage), 1)

        required_marks = round((required_pct / 100.0) * upcoming_max_marks, 1)

        is_achievable = required_pct <= 100.0
        if required_pct <= 0:
            advice = f"Your current performance ({current_avg}%) already secures your goal of {target_average}%!"
            is_achievable = True
            required_marks = 0.0
            required_pct = 0.0
        elif required_pct > 100.0:
            shortfall = required_pct - 100.0
            max_attainable_avg = round((total_weighted_pts + 100.0 * upcoming_weightage) / new_total_weight, 1)
            advice = (
                f"Target of {target_average}% exceeds the maximum possible attainable score. "
                f"Even with a perfect score (100%), your new average will be {max_attainable_avg}%."
            )
        else:
            advice = (
                f"To reach {target_average}% in {subject}, you need to score at least "
                f"{required_marks} / {upcoming_max_marks} ({required_pct}%) in the upcoming assessment."
            )

        return {
            "subject": subject,
            "current_average": current_avg,
            "target_average": target_average,
            "upcoming_max_marks": upcoming_max_marks,
            "required_marks": required_marks,
            "required_percentage": required_pct,
            "is_achievable": is_achievable,
            "advice": advice,
        }

    @staticmethod
    def get_revision_priorities(warning_threshold: float = 60.0) -> List[Dict[str, Any]]:
        """
        Combines subject averages with upcoming exam dates to formulate revision priorities.
        Subjects with low marks and near exam dates are ranked highest.
        """
        summaries = PerformanceAnalyzerService.get_subject_summaries(warning_threshold)["subjects"]
        exams = db.get_all_exams()

        priorities = []
        now = datetime.now()

        for subject, stats in summaries.items():
            # Find nearest exam for this subject
            nearest_exam = None
            days_to_exam = 999.0

            for e in exams:
                if e.subject == subject:
                    try:
                        edt = datetime.strptime(e.exam_date, "%Y-%m-%d")
                        delta = (edt - now).days
                        if 0 <= delta < days_to_exam:
                            days_to_exam = delta
                            nearest_exam = e
                    except Exception:
                        pass

            # Urgency formula: gap below 100 + proximity bonus
            perf_gap = max(0.0, 100.0 - stats["average_percentage"])
            exam_urgency = max(0.0, 30.0 - min(30.0, days_to_exam))

            total_revision_score = round(perf_gap * 0.6 + exam_urgency * 1.5, 1)

            priorities.append({
                "subject": subject,
                "average_percentage": stats["average_percentage"],
                "status": stats["status"],
                "days_to_exam": int(days_to_exam) if days_to_exam < 900 else None,
                "exam_venue": nearest_exam.venue if nearest_exam else None,
                "revision_progress": nearest_exam.revision_progress if nearest_exam else 0.0,
                "priority_score": total_revision_score,
            })

        priorities.sort(key=lambda x: x["priority_score"], reverse=True)
        return priorities
