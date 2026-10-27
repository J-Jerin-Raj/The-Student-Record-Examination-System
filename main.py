#!/usr/bin/env python3
"""
Acadence - Student Academic & Examination Assistant.
Interactive Command-Line Interface (CLI).
Demonstrates CO1 (Stack & Queue), CO2 (Linked List), and CO3 (Search/Sort Complexities).
"""

import sys
import os
from datetime import datetime

import database as db
from models import Task, Exam, Assessment
from services.academic_planner import AcademicPlannerService
from services.exam_manager import ExamManagerService
from services.performance_analyzer import PerformanceAnalyzerService
from services.rescue_mode import AcademicRescueService
from services.priority_engine import PriorityEngine
from services.dsa_lab import DSALabService

# ANSI Colors for styled CLI presentation
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_banner():
    """Render terminal application header."""
    print(f"""{CYAN}{BOLD}
╔════════════════════════════════════════════════════════════════════════════════╗
║    ACADENCE - Academic Productivity & Examination Assistant (CLI)              ║
║    DSA Implementation: CO1 (Stack/Queue) | CO2 (Linked List) | CO3 (Search/Sort)║
║    Flagship Feature: Academic Rescue Mode & Priority Decision Engine           ║
╚════════════════════════════════════════════════════════════════════════════════╝{RESET}""")


def print_table(headers, rows):
    """Render an aligned ASCII table."""
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    header_line = " | ".join(f"{headers[i]:<{col_widths[i]}}" for i in range(len(headers)))
    sep_line = "-+-".join("-" * col_widths[i] for i in range(len(headers)))

    print(f"\n{BOLD}{header_line}{RESET}")
    print(sep_line)
    for row in rows:
        row_str = " | ".join(f"{str(row[i]):<{col_widths[i]}}" for i in range(len(row)))
        print(row_str)
    print()


class AcadenceCLIController:
    """Coordinates terminal workflows across Acadence domain services."""

    def __init__(self):
        db.init_db()
        self.planner = AcademicPlannerService()
        self.exam_mgr = ExamManagerService()

    def show_dashboard(self):
        """Display live academic dashboard status."""
        print(f"\n{BOLD}=== ACADEMIC DASHBOARD SUMMARY ==={RESET}")

        # Exam countdown
        countdown = self.exam_mgr.get_next_exam_countdown()
        if countdown and "exam" in countdown:
            e = countdown["exam"]
            print(f"{CYAN}Nearest Exam : {e['subject']} on {e['exam_date']} ({countdown['days']}d {countdown['hours']}h {countdown['minutes']}m remaining){RESET}")
        else:
            print(f"{YELLOW}No upcoming exams scheduled.{RESET}")

        # Clashes
        conflicts = self.exam_mgr.detect_conflicts()
        if conflicts:
            print(f"{RED}[!] Schedule Conflicts Detected: {len(conflicts)} clash(es) found!{RESET}")
            for c in conflicts:
                print(f"    - {' and '.join(c.get('clashing_subjects', []))} overlap on {c['date']}")
        else:
            print(f"{GREEN}[OK] No examination schedule conflicts detected.{RESET}")

        # Rescue Mode State
        threshold = float(db.get_setting("warning_threshold", "60.0"))
        rescue = AcademicRescueService.analyze_rescue_state(threshold)
        color = RED if rescue["crisis_index"] > 60 else (YELLOW if rescue["crisis_index"] > 30 else GREEN)
        print(f"Crisis Index : {color}{rescue['crisis_index']}/100 ({rescue.get('status_level', '')}){RESET}")
        print(f"Status       : {rescue.get('action_statement', '')}")

        # Top 3 Recommended Actions
        perf = PerformanceAnalyzerService.get_subject_summaries(threshold)
        subject_avgs = {s: d["average_percentage"] for s, d in perf["subjects"].items()}
        all_tasks = db.get_all_tasks()
        ranked = PriorityEngine.rank_tasks(all_tasks, subject_avgs, threshold, include_completed=False)

        if ranked:
            print(f"\n{BOLD}Top Recommended Actions ('What Should I Do Next?'):{RESET}")
            headers = ["Rank", "Task Title", "Subject", "Score", "Effort", "Rationale"]
            rows = []
            for i, item in enumerate(ranked[:3], 1):
                t = item["task"]
                b = item["breakdown"]
                rows.append([
                    str(i),
                    t.title[:32],
                    t.subject[:22],
                    f"{b.total_score:.1f}",
                    f"{t.estimated_effort}h",
                    b.rationale,
                ])
            print_table(headers, rows)

    def manage_tasks(self):
        """View and manage academic tasks."""
        print(f"\n{BOLD}=== TASK PLANNER & PRIORITY ENGINE ==={RESET}")
        print("1. View All Tasks Ranked by Priority Engine")
        print("2. Add New Task")
        print("3. Mark Task as Completed")
        print("4. Delete Task")
        print("5. Generate Daily Study Schedule")

        choice = input(f"\n{BOLD}Select an option (1-5): {RESET}").strip()

        if choice == "1":
            threshold = float(db.get_setting("warning_threshold", "60.0"))
            perf = PerformanceAnalyzerService.get_subject_summaries(threshold)
            subject_avgs = {s: d["average_percentage"] for s, d in perf["subjects"].items()}
            all_tasks = db.get_all_tasks()
            ranked = PriorityEngine.rank_tasks(all_tasks, subject_avgs, threshold, include_completed=True)

            if not ranked:
                print(f"{YELLOW}No tasks found.{RESET}")
                return

            headers = ["ID", "Score", "Title", "Subject", "Deadline", "Effort", "Status"]
            rows = []
            for item in ranked:
                t = item["task"]
                b = item["breakdown"]
                rows.append([
                    str(t.id),
                    f"{b.total_score:.1f}",
                    t.title[:30],
                    t.subject[:20],
                    t.deadline,
                    f"{t.estimated_effort}h",
                    t.status,
                ])
            print_table(headers, rows)

        elif choice == "2":
            title = input("Task Title: ").strip()
            subject = input("Subject: ").strip()
            task_type = input("Type (Assignment, Exam Prep, Project, Lab Work) [Assignment]: ").strip() or "Assignment"
            deadline = input("Deadline (YYYY-MM-DD HH:MM): ").strip()
            effort_str = input("Estimated Effort in Hours [2.0]: ").strip() or "2.0"
            priority = input("Priority (Critical, High, Medium, Low) [Medium]: ").strip() or "Medium"
            notes = input("Notes: ").strip()

            try:
                effort = float(effort_str)
            except ValueError:
                effort = 2.0

            task = Task(
                title=title,
                subject=subject,
                task_type=task_type,
                deadline=deadline,
                estimated_effort=effort,
                priority=priority,
                status="Pending",
                notes=notes,
            )
            success, msg, tid = self.planner.add_task(task)
            if success:
                print(f"{GREEN}[OK] Task #{tid} created successfully! (Recorded on LIFO Undo Stack){RESET}")
            else:
                print(f"{RED}[ERROR] {msg}{RESET}")

        elif choice == "3":
            tid_str = input("Enter Task ID to complete: ").strip()
            if tid_str.isdigit():
                success, msg = self.planner.toggle_status(int(tid_str), "Completed")
                if success:
                    print(f"{GREEN}[OK] Task #{tid_str} marked as Completed! (Undo token pushed){RESET}")
                else:
                    print(f"{RED}[ERROR] Task #{tid_str} not found.{RESET}")

        elif choice == "4":
            tid_str = input("Enter Task ID to delete: ").strip()
            if tid_str.isdigit():
                success, msg = self.planner.delete_task(int(tid_str))
                if success:
                    print(f"{GREEN}[OK] Task #{tid_str} deleted! (Snapshot saved on Undo Stack){RESET}")
                else:
                    print(f"{RED}[ERROR] Task #{tid_str} not found.{RESET}")

        elif choice == "5":
            hours_str = input("Available study hours today [3.5]: ").strip() or "3.5"
            try:
                h = float(hours_str)
            except ValueError:
                h = 3.5

            plan = self.planner.get_suggested_daily_schedule(available_hours=h)
            print(f"\n{BOLD}Recommended Daily Schedule for {plan['available_hours']} hours:{RESET}")
            print(f"Scheduled: {plan['allocated_hours']} hours across {plan['selected_count']} tasks.")

            headers = ["Order", "Task Title", "Subject", "Duration"]
            rows = []
            for idx, item in enumerate(plan["tasks"], 1):
                t = item["task"]
                rows.append([str(idx), t["title"], t["subject"], f"{t['estimated_effort']}h"])
            print_table(headers, rows)

    def undo_action(self):
        """Revert the most recent task modification using LIFO Undo Stack (CO1)."""
        print(f"\n{BOLD}=== LIFO UNDO STACK OPERATION (CO1) ==={RESET}")
        desc = self.planner.peek_undo()
        if not desc:
            print(f"{YELLOW}Undo stack is empty. No recent operations to revert.{RESET}")
            return

        print(f"Top Action on Stack: {CYAN}{desc}{RESET}")
        confirm = input("Execute undo operation? (y/n) [y]: ").strip().lower()
        if confirm in ("", "y", "yes"):
            success, msg = self.planner.undo_last_action()
            if success:
                print(f"{GREEN}[OK] {msg}{RESET}")
            else:
                print(f"{RED}[ERROR] {msg}{RESET}")

    def manage_exams(self):
        """View exams, sort schedules, and detect clashes (CO3)."""
        print(f"\n{BOLD}=== EXAMINATION MANAGEMENT & MERGE SORT (CO3) ==={RESET}")
        exams = self.exam_mgr.get_exams(sort_by="date", algorithm="merge")

        if not exams:
            print(f"{YELLOW}No exams found.{RESET}")
            return

        headers = ["ID", "Subject", "Date", "Time Window", "Venue", "Progress", "Priority"]
        rows = []
        for e in exams:
            rows.append([
                str(e.id),
                e.subject,
                e.exam_date,
                f"{e.start_time} - {e.end_time}",
                e.venue,
                f"{e.revision_progress:.0f}%",
                e.priority,
            ])
        print_table(headers, rows)

        # Clash detection
        conflicts = self.exam_mgr.detect_conflicts()
        if conflicts:
            print(f"{RED}[ALERT] Examination Clashes Detected!{RESET}")
            for c in conflicts:
                print(f"  - {' and '.join(c.get('clashing_subjects', []))} on {c['date']}:")
                print(f"      • {c.get('slot1', '')}")
                print(f"      • {c.get('slot2', '')}")
        else:
            print(f"{GREEN}[OK] Zero examination schedule clashes detected.{RESET}")

    def manage_service_queue(self):
        """Manage academic service requests using custom FIFO Queue (CO1)."""
        print(f"\n{BOLD}=== FIFO ACADEMIC REQUEST QUEUE (CO1) ==={RESET}")
        print("1. View Pending Requests Queue")
        print("2. Submit New Request (Enqueue - O(1))")
        print("3. Process Next Request (Dequeue - O(1))")

        choice = input(f"\n{BOLD}Select an option (1-3): {RESET}").strip()

        if choice == "1":
            pending = self.exam_mgr.get_pending_queue()
            if not pending:
                print(f"{YELLOW}Queue is empty. No pending academic requests.{RESET}")
                return

            headers = ["Order", "Req ID", "Student", "Type", "Subject", "Details"]
            rows = []
            for idx, r in enumerate(pending, 1):
                rows.append([str(idx), r.request_id, r.student_name, r.request_type, r.subject, r.details[:30]])
            print_table(headers, rows)

        elif choice == "2":
            name = input("Student Name [Alex Chen]: ").strip() or "Alex Chen"
            req_type = input("Type (Re-evaluation, Hall Ticket, Doubt Session, Transcript) [Re-evaluation]: ").strip() or "Re-evaluation"
            subject = input("Subject: ").strip()
            details = input("Details: ").strip()

            req = self.exam_mgr.submit_academic_request(name, req_type, subject, details)
            print(f"{GREEN}[OK] Request {req.request_id} enqueued in O(1) time at rear of FIFO queue.{RESET}")

        elif choice == "3":
            processed, msg = self.exam_mgr.process_next_request()
            if processed:
                print(f"{GREEN}[OK] {msg}{RESET}")
            else:
                print(f"{YELLOW}Queue is empty. No pending requests to process.{RESET}")

    def performance_and_target_calculator(self):
        """View subject performance metrics and run target score calculations."""
        print(f"\n{BOLD}=== SUBJECT PERFORMANCE & TARGET SCORE CALCULATOR ==={RESET}")
        threshold = float(db.get_setting("warning_threshold", "60.0"))
        summaries = PerformanceAnalyzerService.get_subject_summaries(threshold)

        headers = ["Subject", "Average", "Assessments", "Status", "Decline Alert"]
        rows = []
        for sname, d in summaries["subjects"].items():
            decline_str = d["decline_reason"] if d["is_declining"] else "None (Stable)"
            rows.append([
                sname,
                f"{d['average_percentage']:.1f}%",
                str(d["assessment_count"]),
                d["status"],
                decline_str,
            ])
        print_table(headers, rows)

        # Target score calculator
        print(f"\n{BOLD}Target Score Calculator (Reverse Sensitivity Analysis):{RESET}")
        target_str = input("Enter target desired percentage [85.0]: ").strip() or "85.0"
        try:
            target_pct = float(target_str)
        except ValueError:
            target_pct = 85.0

        print(f"\nAnalysis for Target {target_pct}%:")
        for sname in summaries["subjects"].keys():
            calc = PerformanceAnalyzerService.calculate_required_score(sname, target_pct, upcoming_max_marks=100.0, upcoming_weightage=40.0)
            status_color = GREEN if calc["is_achievable"] else RED
            print(f"  • {BOLD}{sname}{RESET}: Current {calc['current_average']}%. "
                  f"Required on Final: {status_color}{calc['required_percentage']}%{RESET} "
                  f"({calc['advice']})")

    def run_dsa_lab(self):
        """Run empirical benchmarking trials comparing searching, sorting, and linked lists (CO2 & CO3)."""
        print(f"\n{BOLD}=== INTERACTIVE DSA PERFORMANCE LAB (CO2 & CO3) ==={RESET}")
        print("Running searching benchmarks (Linear Search vs Binary Search on N=2000)...")
        search_res = DSALabService.run_searching_benchmark(size=2000)

        print(f"Dataset Size: {search_res['dataset_size']} elements")
        print(f"  - Linear Search (Array):       {search_res['linear_array']['comparisons']} comparisons in {search_res['linear_array']['time_ms']} ms [{search_res['linear_array']['complexity']}]")
        print(f"  - Linear Search (Linked List): {search_res['linked_list_search']['comparisons']} comparisons in {search_res['linked_list_search']['time_ms']} ms [{search_res['linked_list_search']['complexity']}]")
        print(f"  - Binary Search (Array):       {search_res['binary_search']['comparisons']} comparisons in {search_res['binary_search']['time_ms']} ms [{search_res['binary_search']['complexity']}]")
        print(f"  -> Binary Search Speedup:      {search_res['speedup_factor']}x faster than linear scan!")

        print("\nRunning sorting benchmarks (Bubble Sort vs Insertion Sort vs Merge Sort)...")
        sizes = [100, 300, 700]
        headers = ["N", "Bubble Sort Time", "Insertion Sort Time", "Merge Sort Time"]
        rows = []
        for sz in sizes:
            r = DSALabService.run_sorting_benchmark(size=sz)
            b_time = f"{r['bubble']['time_ms']} ms" if isinstance(r['bubble']['time_ms'], (int, float)) else r['bubble']['time_ms']
            i_time = f"{r['insertion']['time_ms']} ms" if isinstance(r['insertion']['time_ms'], (int, float)) else r['insertion']['time_ms']
            m_time = f"{r['merge']['time_ms']} ms"
            rows.append([str(sz), b_time, i_time, m_time])
        print_table(headers, rows)

        print("Running storage benchmark (Singly Linked List vs Array Head Insertion)...")
        storage_res = DSALabService.run_storage_benchmark(size=2000)
        print(f"Head Insertion (Index 0) on N={storage_res['dataset_size']} records:")
        print(f"  - Singly Linked List: {storage_res['linked_list_head_insert_ms']} ms [O(1) pointer updates]")
        print(f"  - Python List (Array): {storage_res['array_head_insert_ms']} ms [O(n) element shifting]")
        print(f"  -> Linked List Head Insertion Speedup: {storage_res['speedup_ratio']}x faster!")
        print(f"  Note: {storage_res['explanation']}")

    def start(self):
        """Main interaction loop."""
        while True:
            print_banner()
            print("1. Academic Dashboard & Status (Summary, Clash Alerts, Rescue Index)")
            print("2. Task Planner & Priority Engine (View Ranked Tasks, Add, Complete, Schedule)")
            print("3. Undo Last Planner Action (CO1 - LIFO Stack Demonstration)")
            print("4. Examination Manager & Schedule (CO3 - Merge Sort & Clash Detector)")
            print("5. Academic Service Queue (CO1 - FIFO Queue Enqueue & Dequeue)")
            print("6. Subject Performance & Target Score Calculator (Reverse Sensitivity)")
            print("7. Run Interactive DSA Lab Benchmarks (CO2 & CO3 Empirical Analysis)")
            print("8. Reset Database to Default Demo Data")
            print("9. Launch Web Dashboard (python app.py)")
            print("10. Exit Application")

            choice = input(f"\n{BOLD}Enter your choice (1-10): {RESET}").strip()

            if choice == "1":
                self.show_dashboard()
            elif choice == "2":
                self.manage_tasks()
            elif choice == "3":
                self.undo_action()
            elif choice == "4":
                self.manage_exams()
            elif choice == "5":
                self.manage_service_queue()
            elif choice == "6":
                self.performance_and_target_calculator()
            elif choice == "7":
                self.run_dsa_lab()
            elif choice == "8":
                db.clear_all_data()
                db.seed_demo_data()
                print(f"{GREEN}[OK] Database reset and reseeded with default demo data.{RESET}")
            elif choice == "9":
                print(f"\n{GREEN}[OK] To launch the full-stack web application, open a terminal and run:{RESET}")
                print(f"    {BOLD}python app.py{RESET}")
                print(f"    Then open http://localhost:8080 in your browser.")
            elif choice == "10":
                print(f"\n{GREEN}Thank you for using Acadence. Goodbye!{RESET}")
                sys.exit(0)
            else:
                print(f"{RED}[ERROR] Invalid selection. Please enter a number between 1 and 10.{RESET}")

            input(f"\n{CYAN}Press Enter to return to main menu...{RESET}")


if __name__ == "__main__":
    controller = AcadenceCLIController()
    controller.start()
