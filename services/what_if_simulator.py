"""
Novelty Feature: What-If Marks Simulator.
Analyzes student academic marks, identifies performance bottlenecks,
predicts future scores, and calculates exact requirements to reach target grades/GPAs.
Includes an improvement roadmap generator using sensitivity analysis.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import math
from models.student import Student


@dataclass
class SubjectDiagnosis:
    """Diagnostic profile for an individual subject."""
    subject: str
    current_marks: float
    max_marks: float
    status: str  # 'Critical', 'Needs Improvement', 'Proficient', 'Exemplary'
    improvement_headroom: float  # max_marks - current_marks
    recommendation: str


@dataclass
class GoalAnalysisResult:
    """Comprehensive outcome of a goal-setting what-if simulation."""
    student_id: str
    student_name: str
    current_percentage: float
    target_percentage: float
    is_achievable: bool
    max_possible_percentage: float
    required_overall_increase: float
    subject_diagnoses: List[SubjectDiagnosis]
    improvement_plan: List[Dict[str, Any]]
    actionable_advice: str


class WhatIfMarksSimulator:
    """
    Simulation engine to project academic outcomes, calculate target requirements,
    and provide data-driven improvement roadmaps for students.
    """

    @staticmethod
    def diagnose_student(student: Student) -> List[SubjectDiagnosis]:
        """
        Analyze current marks across all subjects and categorize performance.
        Categorization:
        - < 50: Critical (At risk of failure/poor grade)
        - 50 - 69: Needs Improvement
        - 70 - 84: Proficient
        - >= 85: Exemplary
        """
        diagnoses = []
        for subject, marks in student.marks.items():
            headroom = max(0.0, 100.0 - marks)
            if marks < 50:
                status = "Critical"
                rec = f"Urgent remediation needed. Focus on core fundamental topics and schedule tutoring."
            elif marks < 70:
                status = "Needs Improvement"
                rec = f"Significant room for gain (+{headroom:.1f} max). Practice problem-solving and previous year papers."
            elif marks < 85:
                status = "Proficient"
                rec = f"Good grasp. Refine edge cases, test speed, and revision to push towards distinction."
            else:
                status = "Exemplary"
                rec = f"Mastery demonstrated. Maintain consistency through light periodic review."

            diagnoses.append(
                SubjectDiagnosis(
                    subject=subject,
                    current_marks=marks,
                    max_marks=100.0,
                    status=status,
                    improvement_headroom=headroom,
                    recommendation=rec,
                )
            )

        # Sort by improvement headroom descending (subjects with most potential gain first)
        diagnoses.sort(key=lambda d: d.improvement_headroom, reverse=True)
        return diagnoses

    @staticmethod
    def analyze_goal(student: Student, target_percentage: float) -> GoalAnalysisResult:
        """
        Performs reverse sensitivity analysis to compute the exact marks needed
        across subjects to hit a target overall percentage.
        """
        num_subjects = len(student.marks)
        if num_subjects == 0:
            return GoalAnalysisResult(
                student_id=student.student_id,
                student_name=student.name,
                current_percentage=0.0,
                target_percentage=target_percentage,
                is_achievable=False,
                max_possible_percentage=0.0,
                required_overall_increase=0.0,
                subject_diagnoses=[],
                improvement_plan=[],
                actionable_advice="No subjects enrolled for this student.",
            )

        current_total = student.total_marks
        max_total = num_subjects * 100.0
        current_pct = student.percentage

        target_total_needed = (target_percentage / 100.0) * max_total
        delta_marks_needed = target_total_needed - current_total

        diagnoses = WhatIfMarksSimulator.diagnose_student(student)
        total_headroom = sum(d.improvement_headroom for d in diagnoses)
        max_possible_pct = round(((current_total + total_headroom) / max_total) * 100.0, 2)

        # Check feasibility
        if delta_marks_needed <= 0:
            is_achievable = True
            advice = (
                f"You have already achieved {current_pct}%, which meets or exceeds your "
                f"goal of {target_percentage}%. Focus on maintaining your current study rhythm!"
            )
            plan = []
            for d in diagnoses:
                plan.append({
                    "subject": d.subject,
                    "current": d.current_marks,
                    "target_marks": d.current_marks,
                    "delta": 0.0,
                    "strategy": "Maintain performance",
                })

        elif delta_marks_needed > total_headroom:
            is_achievable = False
            shortfall = delta_marks_needed - total_headroom
            advice = (
                f"Target of {target_percentage}% is mathematically unachievable (requires "
                f"+{delta_marks_needed:.1f} marks, but max headroom is +{total_headroom:.1f} marks). "
                f"The highest attainable score is {max_possible_pct}%. Consider aiming for {max_possible_pct}% instead."
            )
            plan = []
            for d in diagnoses:
                plan.append({
                    "subject": d.subject,
                    "current": d.current_marks,
                    "target_marks": 100.0,
                    "delta": d.improvement_headroom,
                    "strategy": "Maximize to 100",
                })

        else:
            is_achievable = True
            advice = (
                f"To boost your overall score from {current_pct}% to {target_percentage}%, "
                f"you need to gain an aggregate of +{delta_marks_needed:.1f} marks across your subjects. "
                f"Below is your optimized subject-by-subject target roadmap."
            )

            # Smart greedy allocation: Distribute needed marks proportionally to headroom
            # (Subjects with lower current marks receive a higher targeted improvement load)
            remaining_delta = delta_marks_needed
            plan = []

            for d in diagnoses:
                if total_headroom > 0:
                    fraction = d.improvement_headroom / total_headroom
                    assigned_boost = round(min(d.improvement_headroom, delta_marks_needed * fraction), 1)
                else:
                    assigned_boost = 0.0

                plan.append({
                    "subject": d.subject,
                    "current": d.current_marks,
                    "target_marks": round(d.current_marks + assigned_boost, 1),
                    "delta": assigned_boost,
                    "strategy": f"Gain +{assigned_boost:.1f} marks (Target: {d.current_marks + assigned_boost:.1f}/100)",
                })

        return GoalAnalysisResult(
            student_id=student.student_id,
            student_name=student.name,
            current_percentage=current_pct,
            target_percentage=target_percentage,
            is_achievable=is_achievable,
            max_possible_percentage=max_possible_pct,
            required_overall_increase=max(0.0, round(delta_marks_needed, 2)),
            subject_diagnoses=diagnoses,
            improvement_plan=plan,
            actionable_advice=advice,
        )

    @staticmethod
    def simulate_custom_scenario(
        student: Student, hypothetical_marks: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Simulate an explicit hypothetical scenario:
        'What if the student scores X in DSA, Y in WebDev, etc.?'
        Calculates predicted total, predicted percentage, new grade, and delta.
        """
        temp_marks = dict(student.marks)
        temp_marks.update(hypothetical_marks)

        hypothetical_student = Student(
            student_id=student.student_id,
            name=student.name,
            department=student.department,
            semester=student.semester,
            marks=temp_marks,
        )

        old_pct = student.percentage
        new_pct = hypothetical_student.percentage
        delta_pct = round(new_pct - old_pct, 2)

        return {
            "student_id": student.student_id,
            "student_name": student.name,
            "original_percentage": old_pct,
            "predicted_percentage": new_pct,
            "percentage_change": delta_pct,
            "original_grade": student.grade,
            "predicted_grade": hypothetical_student.grade,
            "updated_marks": temp_marks,
        }
