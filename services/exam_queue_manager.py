"""
Examination Queue Manager Service (CO1).
Uses the custom FIFO Queue to process student examination activities
(Exam Registration, Hall Ticket Generation, Re-evaluation, Supplementary Application)
in strict first-come, first-served order.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from structures.queue import Queue


@dataclass
class ExamRequest:
    """Represents an examination activity request in the queue."""
    request_id: str
    student_id: str
    student_name: str
    activity_type: str  # e.g., 'Exam Registration', 'Re-evaluation', 'Hall Ticket'
    details: str
    created_at: str
    status: str = "Pending"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "student_id": self.student_id,
            "student_name": self.student_name,
            "activity_type": self.activity_type,
            "details": self.details,
            "created_at": self.created_at,
            "status": self.status,
        }


class ExamQueueManager:
    """
    Manages examination activities using a custom FIFO Queue.
    Ensures fair, sequential processing of student academic requests.
    """

    def __init__(self):
        self.queue = Queue()
        self.processed_history: List[ExamRequest] = []
        self._seq_counter = 1000

    def _generate_id(self) -> str:
        self._seq_counter += 1
        return f"REQ-{self._seq_counter}"

    def submit_request(
        self,
        student_id: str,
        student_name: str,
        activity_type: str,
        details: str = "",
    ) -> ExamRequest:
        """
        Enqueue a new student examination request into the FIFO queue.
        Time Complexity: O(1)
        """
        req_id = self._generate_id()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        req = ExamRequest(
            request_id=req_id,
            student_id=student_id,
            student_name=student_name,
            activity_type=activity_type,
            details=details,
            created_at=timestamp,
            status="Pending",
        )
        self.queue.enqueue(req)
        return req

    def process_next(self) -> Tuple[Optional[ExamRequest], str]:
        """
        Process (dequeue) the request at the front of the queue.
        Time Complexity: O(1)
        """
        if self.queue.is_empty():
            return None, "Queue is empty. No pending examination requests to process."

        req: ExamRequest = self.queue.dequeue()
        req.status = "Processed"
        self.processed_history.append(req)
        return req, f"Successfully processed request {req.request_id} ({req.activity_type}) for {req.student_name}."

    def peek_next(self) -> Optional[ExamRequest]:
        """
        Inspect the next request in line without dequeuing.
        Time Complexity: O(1)
        """
        return self.queue.peek()

    def pending_count(self) -> int:
        """Return the number of requests waiting in the queue."""
        return self.queue.size()

    def get_pending_requests(self) -> List[ExamRequest]:
        """Return all pending requests in FIFO sequence."""
        return self.queue.to_list()

    def get_history(self) -> List[ExamRequest]:
        """Return history of processed requests."""
        return list(self.processed_history)
