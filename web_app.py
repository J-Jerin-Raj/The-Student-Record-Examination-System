#!/usr/bin/env python3
"""
Web Server for DSA Microproject Interactive Dashboard.
Uses Python's standard library `http.server` with zero external dependencies.
Provides RESTful API endpoints and serves a modern responsive UI.
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from models.student import Student
from services.student_manager import StudentManager
from services.exam_queue_manager import ExamQueueManager
from services.what_if_simulator import WhatIfMarksSimulator
from algorithms.searching import (
    linear_search_linked_list,
    linear_search_list,
    binary_search,
)
from algorithms.sorting import (
    bubble_sort,
    insertion_sort,
    merge_sort,
)
from benchmark.performance import (
    benchmark_storage_structures,
    benchmark_searching_algorithms,
    benchmark_sorting_algorithms,
)

# Global instances
student_mgr = StudentManager()
exam_mgr = ExamQueueManager()

# Load sample data
data_file = os.path.join(os.path.dirname(__file__), "data", "sample_students.json")
if os.path.exists(data_file):
    student_mgr.load_from_json(data_file)


class DSADashboardHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status: int = 200, content_type: str = "application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def _read_json_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            body = self.rfile.read(content_length).decode("utf-8")
            return json.loads(body)
        return {}

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/" or path == "/index.html":
            html_path = os.path.join(os.path.dirname(__file__), "web", "index.html")
            if os.path.exists(html_path):
                with open(html_path, "rb") as f:
                    content = f.read()
                self._set_headers(200, "text/html; charset=utf-8")
                self.wfile.write(content)
            else:
                self._set_headers(404, "text/plain")
                self.wfile.write(b"Dashboard HTML file not found.")
            return

        # API Routes
        if path == "/api/students":
            students = student_mgr.get_all_students()
            self._set_headers(200)
            self.wfile.write(json.dumps([s.to_dict() for s in students]).encode("utf-8"))
            return

        if path == "/api/stack":
            # Return undo stack items representation
            actions = student_mgr.undo_stack.to_list()
            serialized = []
            for a in actions:
                serialized.append({
                    "action_type": a.action_type,
                    "student_id": a.student_id,
                    "description": a.description,
                })
            self._set_headers(200)
            self.wfile.write(json.dumps(serialized).encode("utf-8"))
            return

        if path == "/api/queue":
            pending = [r.to_dict() for r in exam_mgr.get_pending_requests()]
            history = [r.to_dict() for r in exam_mgr.get_history()]
            self._set_headers(200)
            self.wfile.write(json.dumps({"pending": pending, "history": history}).encode("utf-8"))
            return

        if path == "/api/search":
            target = query.get("q", [""])[0].strip()
            algo = query.get("algo", ["linear_ll"])[0].strip()

            students_ll = student_mgr.records
            students_list = student_mgr.get_all_students()

            if algo == "linear_ll":
                res = linear_search_linked_list(students_ll, target)
            elif algo == "linear_arr":
                res = linear_search_list(students_list, target)
            elif algo == "binary":
                sorted_list = sorted(students_list, key=lambda s: s.student_id)
                res = binary_search(sorted_list, target)
            else:
                res = linear_search_linked_list(students_ll, target)

            data = {
                "found": res.found,
                "student": res.data.to_dict() if res.data else None,
                "comparisons": res.comparisons,
                "execution_time_ms": res.execution_time_ms,
                "algorithm": res.algorithm,
                "data_structure": res.data_structure,
            }
            self._set_headers(200)
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return

        if path == "/api/sort":
            algo = query.get("algo", ["merge"])[0].strip()
            by = query.get("by", ["marks"])[0].strip()
            order = query.get("order", ["desc"])[0].strip()
            reverse = order.lower() == "desc"

            students = student_mgr.get_all_students()
            if algo == "bubble":
                res = bubble_sort(students, criterion=by, reverse=reverse)
            elif algo == "insertion":
                res = insertion_sort(students, criterion=by, reverse=reverse)
            else:
                res = merge_sort(students, criterion=by, reverse=reverse)

            data = {
                "algorithm": res.algorithm,
                "criterion": res.criterion,
                "reverse": res.reverse,
                "comparisons": res.comparisons,
                "swaps_or_shifts": res.swaps_or_shifts,
                "execution_time_ms": res.execution_time_ms,
                "sorted_students": [s.to_dict() for s in res.sorted_items],
            }
            self._set_headers(200)
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return

        if path == "/api/benchmarks":
            storage = benchmark_storage_structures(n=3000)
            searching = benchmark_searching_algorithms([100, 500, 1000, 3000])
            sorting = benchmark_sorting_algorithms([100, 300, 700, 1200])

            self._set_headers(200)
            self.wfile.write(json.dumps({
                "storage": storage,
                "searching": searching,
                "sorting": sorting,
            }).encode("utf-8"))
            return

        self._set_headers(404)
        self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        body = self._read_json_body()

        if path == "/api/students":
            student = Student.from_dict(body)
            success, msg = student_mgr.add_student(student, push_undo=True)
            status = 201 if success else 400
            self._set_headers(status)
            self.wfile.write(json.dumps({"success": success, "message": msg}).encode("utf-8"))
            return

        if path == "/api/undo":
            success, msg = student_mgr.undo_last_action()
            status = 200 if success else 400
            self._set_headers(status)
            self.wfile.write(json.dumps({"success": success, "message": msg}).encode("utf-8"))
            return

        if path == "/api/queue/enqueue":
            sid = body.get("student_id", "")
            s = student_mgr.get_student_by_id(sid)
            sname = s.name if s else body.get("student_name", "Unknown")
            act_type = body.get("activity_type", "Exam Registration")
            details = body.get("details", "")

            req = exam_mgr.submit_request(sid, sname, act_type, details)
            self._set_headers(201)
            self.wfile.write(json.dumps({"success": True, "request": req.to_dict()}).encode("utf-8"))
            return

        if path == "/api/queue/dequeue":
            req, msg = exam_mgr.process_next()
            status = 200 if req else 400
            self._set_headers(status)
            self.wfile.write(json.dumps({
                "success": req is not None,
                "message": msg,
                "request": req.to_dict() if req else None,
            }).encode("utf-8"))
            return

        if path == "/api/what-if/diagnose":
            sid = body.get("student_id")
            s = student_mgr.get_student_by_id(sid)
            if not s:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Student not found"}).encode("utf-8"))
                return

            diagnoses = WhatIfMarksSimulator.diagnose_student(s)
            data = {
                "student": s.to_dict(),
                "diagnoses": [
                    {
                        "subject": d.subject,
                        "current_marks": d.current_marks,
                        "status": d.status,
                        "headroom": d.improvement_headroom,
                        "recommendation": d.recommendation,
                    }
                    for d in diagnoses
                ],
            }
            self._set_headers(200)
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return

        if path == "/api/what-if/goal":
            sid = body.get("student_id")
            target_pct = float(body.get("target_percentage", 80.0))
            s = student_mgr.get_student_by_id(sid)
            if not s:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Student not found"}).encode("utf-8"))
                return

            res = WhatIfMarksSimulator.analyze_goal(s, target_pct)
            data = {
                "student_id": res.student_id,
                "student_name": res.student_name,
                "current_percentage": res.current_percentage,
                "target_percentage": res.target_percentage,
                "is_achievable": res.is_achievable,
                "max_possible_percentage": res.max_possible_percentage,
                "required_increase": res.required_overall_increase,
                "advice": res.actionable_advice,
                "plan": res.improvement_plan,
            }
            self._set_headers(200)
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return

        if path == "/api/what-if/simulate":
            sid = body.get("student_id")
            hypo_marks = body.get("hypothetical_marks", {})
            s = student_mgr.get_student_by_id(sid)
            if not s:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Student not found"}).encode("utf-8"))
                return

            out = WhatIfMarksSimulator.simulate_custom_scenario(s, hypo_marks)
            self._set_headers(200)
            self.wfile.write(json.dumps(out).encode("utf-8"))
            return

        self._set_headers(404)
        self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path.startswith("/api/students/"):
            sid = path.split("/")[-1].strip().upper()
            success, msg = student_mgr.delete_student(sid, push_undo=True)
            status = 200 if success else 404
            self._set_headers(status)
            self.wfile.write(json.dumps({"success": success, "message": msg}).encode("utf-8"))
            return

        self._set_headers(404)
        self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def log_message(self, format, *args):
        # Clean terminal logging
        sys.stderr.write(f"[Web Server] {self.address_string()} - {format % args}\n")


def run_server(port: int = 8080):
    server_address = ("", port)
    httpd = HTTPServer(server_address, DSADashboardHandler)
    print(f"\n=======================================================")
    print(f"  DSA Microproject Web Dashboard Running!")
    print(f"  Access URL: http://localhost:{port}")
    print(f"  Press Ctrl+C to stop the server.")
    print(f"=======================================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down web server...")
        httpd.server_close()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)
