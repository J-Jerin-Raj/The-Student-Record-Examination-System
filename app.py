#!/usr/bin/env python3
"""
Acadence - Student Academic & Examination Assistant
Main Full-Stack Web Application Server.
Uses Python's standard library http.server with zero external dependencies.
Provides a comprehensive REST API and serves a modern, responsive web dashboard.
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

import database as db
from models import Task, Exam, Assessment
from services.academic_planner import AcademicPlannerService
from services.exam_manager import ExamManagerService
from services.performance_analyzer import PerformanceAnalyzerService
from services.rescue_mode import AcademicRescueService
from services.priority_engine import PriorityEngine
from services.dsa_lab import DSALabService

# Initialize Database
db.init_db()

# Services Singletons
planner_service = AcademicPlannerService()
exam_service = ExamManagerService()


class AcadenceRequestHandler(BaseHTTPRequestHandler):
    """Handles RESTful API requests and static asset delivery."""

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
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length > 0:
                raw_body = self.rfile.read(content_length).decode("utf-8")
                return json.loads(raw_body)
        except Exception:
            pass
        return {}

    def _serve_file(self, file_path: str, content_type: str):
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                data = f.read()
            self._set_headers(200, content_type)
            self.wfile.write(data)
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"404 Not Found")

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # 1. Static Assets & Pages
        if path == "/" or path == "/index.html":
            html_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
            self._serve_file(html_path, "text/html; charset=utf-8")
            return

        if path.startswith("/static/"):
            rel_path = path[len("/static/"):].lstrip("/\\")
            file_path = os.path.join(os.path.dirname(__file__), "static", rel_path)
            if not os.path.exists(file_path):
                if rel_path.endswith(".css"):
                    file_path = os.path.join(os.path.dirname(__file__), "static", "css", rel_path)
                elif rel_path.endswith(".js"):
                    file_path = os.path.join(os.path.dirname(__file__), "static", "js", rel_path)

            ct = "text/css" if rel_path.endswith(".css") else ("application/javascript" if rel_path.endswith(".js") else "text/plain")
            self._serve_file(file_path, ct)
            return

        threshold = float(db.get_setting("warning_threshold", "60.0"))

        # 2. Dashboard Comprehensive API
        if path == "/api/dashboard":
            task_metrics = planner_service.get_task_metrics()
            countdown = exam_service.get_next_exam_countdown()
            conflicts = exam_service.detect_conflicts()
            perf = PerformanceAnalyzerService.get_subject_summaries(threshold)
            rescue_state = AcademicRescueService.analyze_rescue_state(threshold)

            # "What should I do next?" recommendations
            subject_avgs = {s: d["average_percentage"] for s, d in perf["subjects"].items()}
            all_tasks = db.get_all_tasks()
            ranked_tasks = PriorityEngine.rank_tasks(all_tasks, subject_avgs, threshold, include_completed=False)

            data = {
                "task_metrics": task_metrics,
                "next_exam_countdown": countdown,
                "exam_conflicts": conflicts,
                "performance_summary": {
                    "overall_average": perf["overall_average"],
                    "overall_grade": perf["overall_grade"],
                    "vulnerable_subjects_count": len([s for s, d in perf["subjects"].items() if d["status"] in ("Critical", "Vulnerable")]),
                },
                "rescue_summary": {
                    "crisis_index": rescue_state["crisis_index"],
                    "status_level": rescue_state["status_level"],
                    "action_statement": rescue_state["action_statement"],
                },
                "what_to_do_next": [
                    {
                        "task": item["task"].to_dict(),
                        "score": item["score"],
                        "rationale": item["breakdown"].rationale,
                        "is_overdue": item["breakdown"].is_overdue,
                        "hours_remaining": item["breakdown"].hours_remaining,
                    }
                    for item in ranked_tasks[:3]
                ],
            }
            self._set_headers(200)
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return

        # 3. Tasks API
        if path == "/api/tasks":
            status_filter = query.get("status", [None])[0]
            subject_filter = query.get("subject", [None])[0]
            tasks = planner_service.get_tasks(status_filter, subject_filter)

            # Calculate priority breakdown for each task
            perf = PerformanceAnalyzerService.get_subject_summaries(threshold)
            subject_avgs = {s: d["average_percentage"] for s, d in perf["subjects"].items()}

            out = []
            for t in tasks:
                b = PriorityEngine.evaluate_task(t, subject_avgs, threshold)
                d = t.to_dict()
                d["priority_score"] = b.total_score
                d["rationale"] = b.rationale
                d["is_overdue"] = b.is_overdue
                d["hours_remaining"] = b.hours_remaining
                out.append(d)

            self._set_headers(200)
            self.wfile.write(json.dumps(out).encode("utf-8"))
            return

        # 4. Daily Study Schedule API
        if path == "/api/planner/daily-schedule":
            hours = float(query.get("hours", [db.get_setting("daily_study_hours", "3.5")])[0])
            perf = PerformanceAnalyzerService.get_subject_summaries(threshold)
            subject_avgs = {s: d["average_percentage"] for s, d in perf["subjects"].items()}
            schedule = planner_service.get_suggested_daily_schedule(hours, subject_avgs, threshold)
            self._set_headers(200)
            self.wfile.write(json.dumps(schedule).encode("utf-8"))
            return

        # 5. Exams API
        if path == "/api/exams":
            sort_by = query.get("sort_by", ["date"])[0]
            algorithm = query.get("algorithm", ["merge"])[0]
            exams = exam_service.get_exams(sort_by=sort_by, algorithm=algorithm)
            self._set_headers(200)
            self.wfile.write(json.dumps([e.to_dict() for e in exams]).encode("utf-8"))
            return

        if path == "/api/exams/conflicts":
            conflicts = exam_service.detect_conflicts()
            self._set_headers(200)
            self.wfile.write(json.dumps(conflicts).encode("utf-8"))
            return

        if path == "/api/exams/countdown":
            countdown = exam_service.get_next_exam_countdown()
            self._set_headers(200)
            self.wfile.write(json.dumps(countdown).encode("utf-8"))
            return

        # 6. Performance API
        if path == "/api/performance":
            summaries = PerformanceAnalyzerService.get_subject_summaries(threshold)
            self._set_headers(200)
            self.wfile.write(json.dumps(summaries).encode("utf-8"))
            return

        if path == "/api/performance/revision-priorities":
            revs = PerformanceAnalyzerService.get_revision_priorities(threshold)
            self._set_headers(200)
            self.wfile.write(json.dumps(revs).encode("utf-8"))
            return

        # 7. Academic Rescue Mode API
        if path == "/api/rescue":
            rescue_data = AcademicRescueService.analyze_rescue_state(threshold)
            self._set_headers(200)
            self.wfile.write(json.dumps(rescue_data).encode("utf-8"))
            return

        # 8. Undo Stack API
        if path == "/api/undo/peek":
            desc = planner_service.peek_undo()
            self._set_headers(200)
            self.wfile.write(json.dumps({"has_undo": desc is not None, "description": desc}).encode("utf-8"))
            return

        # 9. Requests Queue API
        if path == "/api/requests":
            pending = [r.to_dict() for r in exam_service.get_pending_queue()]
            history = [r.to_dict() for r in exam_service.get_processed_history()]
            self._set_headers(200)
            self.wfile.write(json.dumps({"pending": pending, "history": history}).encode("utf-8"))
            return

        # 10. Settings API
        if path == "/api/settings":
            settings = db.get_all_settings()
            self._set_headers(200)
            self.wfile.write(json.dumps(settings).encode("utf-8"))
            return

        self._set_headers(404)
        self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        body = self._read_json_body()

        # Task Management
        if path == "/api/tasks":
            task = Task.from_dict(body)
            success, msg, tid = planner_service.add_task(task)
            self._set_headers(201 if success else 400)
            self.wfile.write(json.dumps({"success": success, "message": msg, "id": tid}).encode("utf-8"))
            return

        if path.startswith("/api/tasks/") and path.endswith("/status"):
            try:
                task_id = int(path.split("/")[3])
                new_status = body.get("status", "Completed")
                success, msg = planner_service.toggle_status(task_id, new_status)
                self._set_headers(200 if success else 400)
                self.wfile.write(json.dumps({"success": success, "message": msg}).encode("utf-8"))
                return
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
                return

        # Undo Action
        if path == "/api/undo":
            success, msg = planner_service.undo_last_action()
            self._set_headers(200 if success else 400)
            self.wfile.write(json.dumps({"success": success, "message": msg}).encode("utf-8"))
            return

        # Exam Management
        if path == "/api/exams":
            exam = Exam.from_dict(body)
            success, msg, eid = exam_service.add_exam(exam)
            self._set_headers(201 if success else 400)
            self.wfile.write(json.dumps({"success": success, "message": msg, "id": eid}).encode("utf-8"))
            return

        # Assessment Management
        if path == "/api/assessments":
            assessment = Assessment.from_dict(body)
            aid = db.insert_assessment(assessment)
            self._set_headers(201)
            self.wfile.write(json.dumps({"success": True, "id": aid, "message": "Assessment score recorded."}).encode("utf-8"))
            return

        # Target Score Calculator
        if path == "/api/performance/target-score":
            subject = body.get("subject", "")
            target_avg = float(body.get("target_average", 80.0))
            max_m = float(body.get("upcoming_max_marks", 100.0))
            weight = float(body.get("upcoming_weightage", 30.0))
            res = PerformanceAnalyzerService.calculate_required_score(subject, target_avg, max_m, weight)
            self._set_headers(200)
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        # Academic Requests (FIFO Queue)
        if path == "/api/requests":
            name = body.get("student_name", "Student")
            rtype = body.get("request_type", "Re-evaluation")
            subj = body.get("subject", "")
            details = body.get("details", "")
            req = exam_service.submit_academic_request(name, rtype, subj, details)
            self._set_headers(201)
            self.wfile.write(json.dumps({"success": True, "request": req.to_dict()}).encode("utf-8"))
            return

        if path == "/api/requests/process":
            req, msg = exam_service.process_next_request()
            self._set_headers(200 if req else 400)
            self.wfile.write(json.dumps({
                "success": req is not None,
                "message": msg,
                "request": req.to_dict() if req else None,
            }).encode("utf-8"))
            return

        # DSA Lab Benchmarks
        if path == "/api/dsa/search":
            size = int(body.get("size", 1000))
            res = DSALabService.run_searching_benchmark(size)
            self._set_headers(200)
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        if path == "/api/dsa/sort":
            size = int(body.get("size", 1000))
            res = DSALabService.run_sorting_benchmark(size)
            self._set_headers(200)
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        if path == "/api/dsa/storage":
            size = int(body.get("size", 3000))
            res = DSALabService.run_storage_benchmark(size)
            self._set_headers(200)
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        # Database Management / Demo Data
        if path == "/api/admin/reset-demo":
            db.clear_all_data()
            db.seed_demo_data()
            planner_service.refresh_linked_list()
            exam_service._load_requests_into_queue()
            self._set_headers(200)
            self.wfile.write(json.dumps({"success": True, "message": "Demo data reset successfully."}).encode("utf-8"))
            return

        if path == "/api/admin/clear-data":
            db.clear_all_data()
            planner_service.refresh_linked_list()
            exam_service._load_requests_into_queue()
            self._set_headers(200)
            self.wfile.write(json.dumps({"success": True, "message": "All data cleared."}).encode("utf-8"))
            return

        # Settings
        if path == "/api/settings":
            for k, v in body.items():
                db.set_setting(k, str(v))
            self._set_headers(200)
            self.wfile.write(json.dumps({"success": True, "message": "Settings saved."}).encode("utf-8"))
            return

        self._set_headers(404)
        self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def do_PUT(self):
        parsed = urlparse(self.path)
        path = parsed.path
        body = self._read_json_body()

        if path.startswith("/api/tasks/"):
            try:
                task_id = int(path.split("/")[3])
                task = Task.from_dict(body)
                task.id = task_id
                success, msg = planner_service.update_task(task)
                self._set_headers(200 if success else 400)
                self.wfile.write(json.dumps({"success": success, "message": msg}).encode("utf-8"))
                return
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
                return

        if path.startswith("/api/exams/"):
            try:
                exam_id = int(path.split("/")[3])
                exam = Exam.from_dict(body)
                exam.id = exam_id
                success, msg = exam_service.update_exam(exam)
                self._set_headers(200 if success else 400)
                self.wfile.write(json.dumps({"success": success, "message": msg}).encode("utf-8"))
                return
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
                return

        self._set_headers(404)
        self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/tasks/"):
            try:
                task_id = int(path.split("/")[3])
                success, msg = planner_service.delete_task(task_id)
                self._set_headers(200 if success else 404)
                self.wfile.write(json.dumps({"success": success, "message": msg}).encode("utf-8"))
                return
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
                return

        if path.startswith("/api/exams/"):
            try:
                exam_id = int(path.split("/")[3])
                success, msg = exam_service.delete_exam(exam_id)
                self._set_headers(200 if success else 404)
                self.wfile.write(json.dumps({"success": success, "message": msg}).encode("utf-8"))
                return
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
                return

        if path.startswith("/api/assessments/"):
            try:
                aid = int(path.split("/")[3])
                success = db.delete_assessment(aid)
                self._set_headers(200 if success else 404)
                self.wfile.write(json.dumps({"success": success, "message": "Assessment deleted."}).encode("utf-8"))
                return
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
                return

        self._set_headers(404)
        self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def log_message(self, format, *args):
        # Quiet clean logging
        pass


def run(port: int = 8080):
    server = HTTPServer(("", port), AcadenceRequestHandler)
    print("=" * 65)
    print("  Acadence - Student Academic & Examination Assistant")
    print(f"  Server active at: http://localhost:{port}")
    print("  Press Ctrl+C to stop.")
    print("=" * 65)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.server_close()


if __name__ == "__main__":
    p = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run(p)
