"""
Examination Management Service.
Handles exam scheduling, countdown calculations, syllabus revision tracking,
FIFO Academic Request Queue processing (CO1), and Schedule Conflict Detection.
"""

from datetime import datetime, time as dtime
from typing import Any, Dict, List, Optional, Tuple
from models import Exam, AcademicRequest
import database as db
from data_structures.queue import Queue
from algorithms.searching import linear_search
from algorithms.sorting import bubble_sort, insertion_sort, merge_sort


class ExamManagerService:
    """Manages examinations, conflict detection, and academic request queues."""

    def __init__(self):
        self.request_queue = Queue()
        self.processed_requests: List[AcademicRequest] = []
        self._load_requests_into_queue()

    def _load_requests_into_queue(self):
        """Populate in-memory FIFO queue with pending database requests."""
        self.request_queue.clear()
        reqs = db.get_all_requests()
        for r in reqs:
            if r.status == "Pending":
                self.request_queue.enqueue(r)
            else:
                self.processed_requests.append(r)

    def get_exams(self, sort_by: str = "date", algorithm: str = "merge") -> List[Exam]:
        """Fetch all exams sorted using our manual DSA sorting algorithms (CO3)."""
        exams = db.get_all_exams()
        if not exams:
            return []

        # Key extractor
        if sort_by == "subject":
            key_fn = lambda e: e.subject.lower()
            reverse = False
        elif sort_by == "priority":
            p_order = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
            key_fn = lambda e: p_order.get(e.priority, 1)
            reverse = True
        elif sort_by == "revision":
            key_fn = lambda e: e.revision_progress
            reverse = False  # lowest revision first
        else:  # date
            key_fn = lambda e: f"{e.exam_date} {e.start_time}"
            reverse = False

        if algorithm == "bubble":
            res = bubble_sort(exams, key_func=key_fn, reverse=reverse)
        elif algorithm == "insertion":
            res = insertion_sort(exams, key_func=key_fn, reverse=reverse)
        else:
            res = merge_sort(exams, key_func=key_fn, reverse=reverse)

        return res.sorted_items

    def add_exam(self, exam: Exam) -> Tuple[bool, str, Optional[int]]:
        """Add new exam and check for scheduling conflicts."""
        try:
            eid = db.insert_exam(exam)
            exam.id = eid

            # Check conflicts
            conflicts = self.detect_conflicts()
            has_conflict = any(exam.subject in c["clashing_subjects"] for c in conflicts)
            msg = f"Exam for '{exam.subject}' scheduled on {exam.exam_date} ({exam.start_time} - {exam.end_time})."
            if has_conflict:
                msg += " Warning: A schedule clash was detected for this slot!"

            return True, msg, eid
        except Exception as e:
            return False, f"Failed to schedule exam: {str(e)}", None

    def update_exam(self, exam: Exam) -> Tuple[bool, str]:
        """Update existing examination details."""
        if exam.id is None:
            return False, "Exam ID required."
        try:
            success = db.update_exam(exam)
            return success, "Exam details updated successfully." if success else "Exam not found."
        except Exception as e:
            return False, f"Update failed: {str(e)}"

    def delete_exam(self, exam_id: int) -> Tuple[bool, str]:
        """Remove exam from schedule."""
        try:
            success = db.delete_exam(exam_id)
            return success, "Exam removed from schedule." if success else "Exam not found."
        except Exception as e:
            return False, f"Deletion failed: {str(e)}"

    def detect_conflicts(self) -> List[Dict[str, Any]]:
        """
        Algorithm to detect overlapping examination schedules.
        Compares all pairwise exam slots to identify time clashes on the same date.
        """
        exams = db.get_all_exams()
        conflicts = []
        n = len(exams)

        for i in range(n):
            for j in range(i + 1, n):
                e1 = exams[i]
                e2 = exams[j]

                # Check if dates match
                if e1.exam_date == e2.exam_date:
                    try:
                        # Parse start and end times
                        fmt = "%H:%M"
                        s1 = datetime.strptime(e1.start_time, fmt).time()
                        e1_end = datetime.strptime(e1.end_time, fmt).time()

                        s2 = datetime.strptime(e2.start_time, fmt).time()
                        e2_end = datetime.strptime(e2.end_time, fmt).time()

                        # Two intervals [s1, e1_end] and [s2, e2_end] overlap if max(s1, s2) < min(e1_end, e2_end)
                        if max(s1, s2) < min(e1_end, e2_end):
                            conflicts.append({
                                "date": e1.exam_date,
                                "exam1_id": e1.id,
                                "exam2_id": e2.id,
                                "clashing_subjects": [e1.subject, e2.subject],
                                "slot1": f"{e1.subject}: {e1.start_time} - {e1.end_time} ({e1.venue})",
                                "slot2": f"{e2.subject}: {e2.start_time} - {e2.end_time} ({e2.venue})",
                                "severity": "Critical Clash",
                            })
                    except Exception:
                        pass

        return conflicts

    def get_next_exam_countdown(self) -> Optional[Dict[str, Any]]:
        """
        Finds the nearest upcoming examination and calculates the exact countdown.
        """
        exams = db.get_all_exams()
        now = datetime.now()
        upcoming = []

        for e in exams:
            try:
                dt_str = f"{e.exam_date} {e.start_time}"
                dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
                if dt >= now:
                    upcoming.append((dt, e))
            except Exception:
                pass

        if not upcoming:
            return None

        upcoming.sort(key=lambda x: x[0])
        next_dt, next_exam = upcoming[0]
        diff = next_dt - now

        total_sec = max(0, int(diff.total_seconds()))
        days = total_sec // 86400
        hours = (total_sec % 86400) // 3600
        minutes = (total_sec % 3600) // 60
        seconds = total_sec % 60

        return {
            "exam": next_exam.to_dict(),
            "target_datetime": next_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "total_seconds": total_sec,
            "total_hours": round(total_sec / 3600.0, 1),
            "is_imminent": total_sec < (48 * 3600),
        }

    # ----------------- FIFO Queue Operations (CO1) -----------------

    def submit_academic_request(
        self,
        student_name: str,
        request_type: str,
        subject: str,
        details: str,
    ) -> AcademicRequest:
        """
        Enqueue academic request into FIFO queue and persist in database.
        Time Complexity: O(1)
        """
        seq = db.get_all_requests()
        req_id = f"REQ-{1000 + len(seq) + 1}"
        req = AcademicRequest(
            request_id=req_id,
            student_name=student_name,
            request_type=request_type,
            subject=subject,
            details=details,
            status="Pending",
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        db_id = db.insert_academic_request(req)
        req.id = db_id

        # Enqueue into custom FIFO Queue
        self.request_queue.enqueue(req)
        return req

    def process_next_request(self) -> Tuple[Optional[AcademicRequest], str]:
        """
        Dequeue and process the head request in FIFO order.
        Time Complexity: O(1)
        """
        if self.request_queue.is_empty():
            return None, "Examination request queue is empty. No pending items."

        req: AcademicRequest = self.request_queue.dequeue()
        req.status = "Processed"
        db.update_request_status(req.request_id, "Processed")
        self.processed_requests.insert(0, req)

        return req, f"Processed request {req.request_id} ({req.request_type}) for {req.student_name} in FIFO sequence."

    def peek_next_request(self) -> Optional[AcademicRequest]:
        """Inspect the front request without removing it."""
        return self.request_queue.front()

    def get_pending_queue(self) -> List[AcademicRequest]:
        """Return snapshot of items currently in the FIFO queue."""
        return self.request_queue.to_list()

    def get_processed_history(self) -> List[AcademicRequest]:
        """Return history of processed requests."""
        return list(self.processed_requests)
