#!/usr/bin/env python3
"""
Student Academic Record Management & Examination Processing System.
DSA Microproject covering CO1, CO2, CO3 + Novelty (What-If Marks Simulator).
Interactive Menu-Driven Console Interface.
"""

import os
import sys
import time
from typing import Dict, List, Optional

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
    generate_benchmark_summary_text,
)

# ANSI Colors for formatted CLI output
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_banner():
    banner = f"""{CYAN}{BOLD}
╔════════════════════════════════════════════════════════════════════════════════╗
║    STUDENT RECORD & EXAMINATION SYSTEM (DSA MICROPROJECT)                      ║
║    Covers: CO1 (Stack/Queue) | CO2 (Linked List) | CO3 (Search/Sort Complexities)║
║    Novelty: What-If Marks Simulator & Academic Goal Planner                    ║
╚════════════════════════════════════════════════════════════════════════════════╝{RESET}"""
    print(banner)


def print_table(headers: List[str], rows: List[List[str]], col_widths: Optional[List[int]] = None):
    """Helper to render aligned ASCII tables."""
    if not col_widths:
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


class AppController:
    def __init__(self):
        self.student_mgr = StudentManager()
        self.exam_mgr = ExamQueueManager()
        self.data_path = os.path.join(os.path.dirname(__file__), "data", "sample_students.json")
        self.load_initial_data()

    def load_initial_data(self):
        if os.path.exists(self.data_path):
            count = self.student_mgr.load_from_json(self.data_path)
            print(f"{GREEN}[OK] Pre-loaded {count} student records from sample dataset into Singly Linked List.{RESET}")
        else:
            print(f"{YELLOW}[INFO] Sample data not found. Initialized with empty student records.{RESET}")

    def display_all_students(self):
        students = self.student_mgr.get_all_students()
        if not students:
            print(f"{YELLOW}[INFO] No student records stored in the Linked List.{RESET}")
            return

        headers = ["ID", "Name", "Dept", "Sem", "Marks Breakdown", "Total", "Pct (%)", "Grade"]
        rows = []
        for s in students:
            marks_str = ", ".join(f"{k}:{v}" for k, v in s.marks.items())
            rows.append([
                s.student_id,
                s.name,
                s.department,
                str(s.semester),
                marks_str,
                f"{s.total_marks:.1f}",
                f"{s.percentage:.1f}%",
                s.grade,
            ])
        print_table(headers, rows)
        print(f"{CYAN}Total Records Stored in Singly Linked List: {len(students)}{RESET}")

    def add_student_flow(self):
        print(f"\n{BOLD}--- Add New Student Record (CO2: Linked List Insert) ---{RESET}")
        student_id = input("Enter Student ID (e.g. STU111): ").strip().upper()
        if not student_id:
            print(f"{RED}[ERROR] ID cannot be empty.{RESET}")
            return

        name = input("Enter Full Name: ").strip()
        dept = input("Enter Department (default: CSE): ").strip() or "CSE"
        try:
            sem = int(input("Enter Semester (default: 3): ").strip() or "3")
        except ValueError:
            sem = 3

        print("Enter marks out of 100 for subjects (Enter empty subject name when done):")
        marks = {}
        standard_subjects = ["DSA", "WebDev", "OS", "Maths", "DBMS"]
        for sub in standard_subjects:
            val_str = input(f"  Marks for {sub} [0-100] (press enter to skip): ").strip()
            if val_str:
                try:
                    val = float(val_str)
                    marks[sub] = max(0.0, min(100.0, val))
                except ValueError:
                    pass

        student = Student(student_id=student_id, name=name, department=dept, semester=sem, marks=marks)
        success, msg = self.student_mgr.add_student(student, push_undo=True)
        if success:
            print(f"{GREEN}[OK] {msg} (Pushed to Undo Stack){RESET}")
        else:
            print(f"{RED}[ERROR] {msg}{RESET}")

    def update_student_flow(self):
        print(f"\n{BOLD}--- Update Student Record (CO2: Linked List Update) ---{RESET}")
        student_id = input("Enter Student ID to update: ").strip().upper()
        existing = self.student_mgr.get_student_by_id(student_id)
        if not existing:
            print(f"{RED}[ERROR] Student '{student_id}' not found.{RESET}")
            return

        print(f"Current Record: {existing.name} | Dept: {existing.department} | Marks: {existing.marks}")
        name = input(f"Enter new name (leave blank to keep '{existing.name}'): ").strip() or existing.name
        dept = input(f"Enter new department (leave blank to keep '{existing.department}'): ").strip() or existing.department

        new_marks = dict(existing.marks)
        print("Update subject marks (leave blank to keep current):")
        for sub, curr_val in existing.marks.items():
            val_str = input(f"  {sub} [current: {curr_val}]: ").strip()
            if val_str:
                try:
                    new_marks[sub] = float(val_str)
                except ValueError:
                    pass

        updated = Student(student_id=student_id, name=name, department=dept, semester=existing.semester, marks=new_marks)
        success, msg = self.student_mgr.update_student(student_id, updated, push_undo=True)
        if success:
            print(f"{GREEN}[OK] {msg} (Previous state preserved on Undo Stack){RESET}")
        else:
            print(f"{RED}[ERROR] {msg}{RESET}")

    def delete_student_flow(self):
        print(f"\n{BOLD}--- Delete Student Record (CO2: Linked List Delete) ---{RESET}")
        student_id = input("Enter Student ID to delete: ").strip().upper()
        success, msg = self.student_mgr.delete_student(student_id, push_undo=True)
        if success:
            print(f"{GREEN}[OK] {msg} (Snapshot pushed to Undo Stack){RESET}")
        else:
            print(f"{RED}[ERROR] {msg}{RESET}")

    def undo_flow(self):
        print(f"\n{BOLD}--- Undo Operation (CO1: LIFO Stack) ---{RESET}")
        top_action = self.student_mgr.peek_undo()
        if not top_action:
            print(f"{YELLOW}[INFO] Undo stack is empty. No operations to undo.{RESET}")
            return

        print(f"Next action on top of stack: {CYAN}{top_action}{RESET}")
        confirm = input("Revert this action? (y/N): ").strip().lower()
        if confirm == "y":
            success, msg = self.student_mgr.undo_last_action()
            if success:
                print(f"{GREEN}[OK] {msg}{RESET}")
            else:
                print(f"{RED}[ERROR] {msg}{RESET}")
        else:
            print("Undo cancelled.")

    def search_flow(self):
        print(f"\n{BOLD}--- Search Student (CO2 Linear Search & CO3 Binary Search) ---{RESET}")
        print("1. Linear Search on Singly Linked List (Sequential O(n))")
        print("2. Linear Search on Python List (Sequential O(n))")
        print("3. Binary Search on Sorted Array (Divide & Conquer O(log n))")
        print("4. Compare Linear vs Binary Search side-by-side")

        choice = input("Select search option (1-4): ").strip()
        target_id = input("Enter Student ID to find (e.g. STU105): ").strip().upper()

        students_ll = self.student_mgr.records
        students_list = self.student_mgr.get_all_students()

        if choice == "1":
            res = linear_search_linked_list(students_ll, target_id)
            self._print_search_result(res)
        elif choice == "2":
            res = linear_search_list(students_list, target_id)
            self._print_search_result(res)
        elif choice == "3":
            # Sort array by student ID first
            sorted_list = sorted(students_list, key=lambda s: s.student_id)
            res = binary_search(sorted_list, target_id)
            self._print_search_result(res)
        elif choice == "4":
            sorted_list = sorted(students_list, key=lambda s: s.student_id)
            res_ll = linear_search_linked_list(students_ll, target_id)
            res_arr = linear_search_list(students_list, target_id)
            res_bin = binary_search(sorted_list, target_id)

            print(f"\n{BOLD}Search Comparison for Target: {target_id}{RESET}")
            headers = ["Algorithm", "Data Structure", "Found?", "Comparisons", "Time (ms)"]
            rows = [
                ["Linear Search", "Singly Linked List", str(res_ll.found), str(res_ll.comparisons), f"{res_ll.execution_time_ms:.4f}"],
                ["Linear Search", "Python Array/List", str(res_arr.found), str(res_arr.comparisons), f"{res_arr.execution_time_ms:.4f}"],
                ["Binary Search", "Sorted Array", str(res_bin.found), str(res_bin.comparisons), f"{res_bin.execution_time_ms:.4f}"],
            ]
            print_table(headers, rows)
            print(f"{CYAN}Notice: Binary Search finds the record in logarithmic steps O(log n)!{RESET}")

    def _print_search_result(self, res):
        if res.found and res.data:
            s = res.data
            print(f"{GREEN}[OK] Record Found via {res.algorithm} on {res.data_structure}!{RESET}")
            print(f"    Student: {s.name} ({s.student_id}) | Dept: {s.department} | Pct: {s.percentage}% | Grade: {s.grade}")
            print(f"    Comparisons performed: {res.comparisons} | Execution Time: {res.execution_time_ms:.4f} ms")
        else:
            print(f"{RED}[ERROR] Target not found after {res.comparisons} comparisons ({res.execution_time_ms:.4f} ms).{RESET}")

    def sort_and_ranking_flow(self):
        print(f"\n{BOLD}--- Sorting & Merit List Generation (CO3) ---{RESET}")
        print("Choose Sorting Algorithm:")
        print("1. Bubble Sort (O(n^2) Comparison-based)")
        print("2. Insertion Sort (O(n^2) Incremental)")
        print("3. Merge Sort (O(n log n) Divide-and-Conquer)")
        print("4. Run all three and compare metrics")

        algo_choice = input("Select algorithm (1-4): ").strip()
        crit = input("Sort by: [1] Marks (Merit List), [2] Name, [3] Student ID: ").strip()
        criterion_map = {"1": "marks", "2": "name", "3": "id"}
        criterion = criterion_map.get(crit, "marks")

        rev_str = input("Order: [1] Descending (Highest First), [2] Ascending (Lowest First): ").strip()
        reverse = rev_str != "2"

        students = self.student_mgr.get_all_students()
        if not students:
            print(f"{YELLOW}[INFO] No students available to sort.{RESET}")
            return

        if algo_choice == "1":
            res = bubble_sort(students, criterion=criterion, reverse=reverse)
            self._display_sort_result(res)
        elif algo_choice == "2":
            res = insertion_sort(students, criterion=criterion, reverse=reverse)
            self._display_sort_result(res)
        elif algo_choice == "3":
            res = merge_sort(students, criterion=criterion, reverse=reverse)
            self._display_sort_result(res)
        elif algo_choice == "4":
            res_b = bubble_sort(students, criterion=criterion, reverse=reverse)
            res_i = insertion_sort(students, criterion=criterion, reverse=reverse)
            res_m = merge_sort(students, criterion=criterion, reverse=reverse)

            print(f"\n{BOLD}--- Sorting Algorithm Comparison (Criterion: {criterion.upper()}) ---{RESET}")
            headers = ["Algorithm", "Time Complexity", "Comparisons", "Swaps/Moves", "Time (ms)"]
            rows = [
                ["Bubble Sort", "O(n^2)", str(res_b.comparisons), str(res_b.swaps_or_shifts), f"{res_b.execution_time_ms:.4f}"],
                ["Insertion Sort", "O(n^2)", str(res_i.comparisons), str(res_i.swaps_or_shifts), f"{res_i.execution_time_ms:.4f}"],
                ["Merge Sort", "O(n log n)", str(res_m.comparisons), str(res_m.swaps_or_shifts), f"{res_m.execution_time_ms:.4f}"],
            ]
            print_table(headers, rows)
            self._display_sort_result(res_m)

    def _display_sort_result(self, res):
        print(f"\n{BOLD}Sorted Results using {res.algorithm} ({res.criterion.upper()}, reverse={res.reverse}):{RESET}")
        print(f"Metrics: {res.comparisons} comparisons | {res.swaps_or_shifts} swaps/shifts | Runtime: {res.execution_time_ms:.4f} ms")
        headers = ["Rank", "ID", "Name", "Total Marks", "Percentage", "Grade"]
        rows = []
        for rank, s in enumerate(res.sorted_items, 1):
            rows.append([
                str(rank),
                s.student_id,
                s.name,
                f"{s.total_marks:.1f}",
                f"{s.percentage:.1f}%",
                s.grade,
            ])
        print_table(headers, rows)

    def exam_queue_flow(self):
        while True:
            print(f"\n{BOLD}--- Examination Activity Queue (CO1: FIFO Queue) ---{RESET}")
            print(f"Current Queue Status: {self.exam_mgr.pending_count()} pending requests.")
            print("1. Enqueue New Exam Request")
            print("2. Dequeue & Process Front Request (FIFO)")
            print("3. Peek Front Request")
            print("4. View All Pending Requests")
            print("5. View Processed History")
            print("6. Back to Main Menu")

            ch = input("Enter choice (1-6): ").strip()
            if ch == "1":
                sid = input("Enter Student ID: ").strip().upper()
                s = self.student_mgr.get_student_by_id(sid)
                name = s.name if s else input("Enter Student Name: ").strip()

                print("Select Activity Type:")
                print("  [1] Exam Registration")
                print("  [2] Hall Ticket Issuance")
                print("  [3] Grade Re-evaluation")
                print("  [4] Supplementary Application")
                type_map = {
                    "1": "Exam Registration",
                    "2": "Hall Ticket Issuance",
                    "3": "Grade Re-evaluation",
                    "4": "Supplementary Application",
                }
                act_type = type_map.get(input("Choose activity (1-4): ").strip(), "Exam Registration")
                details = input("Enter request details/remarks: ").strip()

                req = self.exam_mgr.submit_request(sid, name, act_type, details)
                print(f"{GREEN}[OK] Request {req.request_id} enqueued at rear of Queue.{RESET}")

            elif ch == "2":
                req, msg = self.exam_mgr.process_next()
                if req:
                    print(f"{GREEN}[OK] {msg}{RESET}")
                else:
                    print(f"{YELLOW}[INFO] {msg}{RESET}")

            elif ch == "3":
                req = self.exam_mgr.peek_next()
                if req:
                    print(f"{CYAN}Front Request: {req.request_id} | {req.student_name} | {req.activity_type} | Time: {req.created_at}{RESET}")
                else:
                    print(f"{YELLOW}[INFO] Queue is currently empty.{RESET}")

            elif ch == "4":
                pending = self.exam_mgr.get_pending_requests()
                if not pending:
                    print(f"{YELLOW}[INFO] Queue is empty.{RESET}")
                else:
                    headers = ["Position", "Request ID", "Student ID", "Student Name", "Activity", "Details", "Submitted At"]
                    rows = [[str(i), r.request_id, r.student_id, r.student_name, r.activity_type, r.details, r.created_at] for i, r in enumerate(pending, 1)]
                    print_table(headers, rows)

            elif ch == "5":
                history = self.exam_mgr.get_history()
                if not history:
                    print(f"{YELLOW}[INFO] No processed requests in history yet.{RESET}")
                else:
                    headers = ["Request ID", "Student ID", "Name", "Activity", "Status", "Timestamp"]
                    rows = [[r.request_id, r.student_id, r.student_name, r.activity_type, r.status, r.created_at] for r in history]
                    print_table(headers, rows)

            elif ch == "6":
                break

    def what_if_simulator_flow(self):
        print(f"\n{BOLD}═══════════════════════════════════════════════════════════════════{RESET}")
        print(f"{MAGENTA}{BOLD}   NOVELTY: WHAT-IF MARKS SIMULATOR & ACADEMIC GOAL PLANNER        {RESET}")
        print(f"{BOLD}═══════════════════════════════════════════════════════════════════{RESET}")
        print("1. Subject Diagnostics & Weakness Identification")
        print("2. Target Goal Planning (Calculate Required Marks to Reach Target %)")
        print("3. Hypothetical Scenario Tester ('What if I score X in Subject Y?')")

        choice = input("Select simulator mode (1-3): ").strip()
        sid = input("Enter Student ID to analyze (e.g. STU102): ").strip().upper()
        student = self.student_mgr.get_student_by_id(sid)

        if not student:
            print(f"{RED}[ERROR] Student '{sid}' not found.{RESET}")
            return

        print(f"\nAnalyzing: {BOLD}{student.name}{RESET} ({student.student_id}) | Current Score: {CYAN}{student.percentage}% ({student.grade}){RESET}")

        if choice == "1":
            diagnoses = WhatIfMarksSimulator.diagnose_student(student)
            headers = ["Subject", "Current Marks", "Status", "Improvement Headroom", "Actionable Recommendation"]
            rows = []
            for d in diagnoses:
                status_color = RED if d.status == "Critical" else (YELLOW if d.status == "Needs Improvement" else GREEN)
                rows.append([
                    d.subject,
                    f"{d.current_marks}/100",
                    f"{status_color}{d.status}{RESET}",
                    f"+{d.improvement_headroom:.1f}",
                    d.recommendation,
                ])
            print_table(headers, rows)

        elif choice == "2":
            try:
                target_pct = float(input(f"Enter target overall percentage (Current: {student.percentage}%): ").strip())
            except ValueError:
                print(f"{RED}[ERROR] Invalid percentage.{RESET}")
                return

            result = WhatIfMarksSimulator.analyze_goal(student, target_pct)
            print(f"\n{BOLD}--- Goal Analysis Result for {student.name} ---{RESET}")
            print(f"Current Percentage : {result.current_percentage}%")
            print(f"Target Percentage  : {result.target_percentage}%")
            print(f"Goal Achievable?   : {GREEN+'YES' if result.is_achievable else RED+'NO'}{RESET}")
            print(f"Max Possible %     : {result.max_possible_percentage}%")
            print(f"\n{BOLD}Actionable Advice:{RESET}\n{CYAN}{result.actionable_advice}{RESET}\n")

            if result.improvement_plan:
                headers = ["Subject", "Current", "Required Target", "Marks Gain (+)", "Strategy"]
                rows = []
                for p in result.improvement_plan:
                    rows.append([
                        p["subject"],
                        f"{p['current']:.1f}",
                        f"{p['target_marks']:.1f}",
                        f"+{p['delta']:.1f}",
                        p["strategy"],
                    ])
                print_table(headers, rows)

        elif choice == "3":
            print(f"Enter hypothetical new scores for subjects (leave blank to keep current):")
            hypothetical = {}
            for sub, curr in student.marks.items():
                val = input(f"  {sub} [current: {curr}]: ").strip()
                if val:
                    try:
                        hypothetical[sub] = float(val)
                    except ValueError:
                        pass

            sim_out = WhatIfMarksSimulator.simulate_custom_scenario(student, hypothetical)
            print(f"\n{BOLD}--- Simulation Outcome ---{RESET}")
            print(f"Original Percentage : {sim_out['original_percentage']}% ({sim_out['original_grade']})")
            print(f"Predicted Percentage: {CYAN}{sim_out['predicted_percentage']}% ({sim_out['predicted_grade']}){RESET}")
            change = sim_out["percentage_change"]
            color = GREEN if change >= 0 else RED
            print(f"Net Change          : {color}{'+' if change >= 0 else ''}{change}%{RESET}")

    def run_benchmarks_flow(self):
        print(f"\n{BOLD}Running empirical data structure and algorithm benchmarks...{RESET}")
        summary_text = generate_benchmark_summary_text()
        print(summary_text)

    def start(self):
        while True:
            print_banner()
            print("1. [CO2] View All Student Records (Singly Linked List)")
            print("2. [CO2] Add Student Record")
            print("3. [CO2] Update Student Record")
            print("4. [CO2] Delete Student Record")
            print("5. [CO1] Undo Last Record Change (LIFO Stack)")
            print("6. [CO2/CO3] Search Students (Linear vs Binary Search)")
            print("7. [CO3] Sort Students / Merit List (Bubble, Insertion, Merge Sort)")
            print("8. [CO1] Examination Queue Activities (FIFO Queue)")
            print("9. [NOVELTY] What-If Marks Simulator & Goal Planner")
            print("10. [BENCHMARK] Run Comprehensive Performance Analysis")
            print("11. [WEB] Launch Interactive Web Dashboard (Zero External Deps)")
            print("12. Exit Application")

            choice = input(f"\n{BOLD}Enter your choice (1-12): {RESET}").strip()

            if choice == "1":
                self.display_all_students()
            elif choice == "2":
                self.add_student_flow()
            elif choice == "3":
                self.update_student_flow()
            elif choice == "4":
                self.delete_student_flow()
            elif choice == "5":
                self.undo_flow()
            elif choice == "6":
                self.search_flow()
            elif choice == "7":
                self.sort_and_ranking_flow()
            elif choice == "8":
                self.exam_queue_flow()
            elif choice == "9":
                self.what_if_simulator_flow()
            elif choice == "10":
                self.run_benchmarks_flow()
            elif choice == "11":
                print(f"\n{GREEN}[OK] To launch the Web Dashboard, open a new terminal and run:{RESET}")
                print(f"    {BOLD}python3 web_app.py{RESET}")
                print(f"    Then open http://localhost:8080 in your browser.")
            elif choice == "12":
                # Save records before exit
                self.student_mgr.save_to_json(self.data_path)
                print(f"{GREEN}[OK] Saved records to database. Exiting. Goodbye!{RESET}")
                sys.exit(0)
            else:
                print(f"{RED}[ERROR] Invalid option. Please enter a number between 1 and 12.{RESET}")

            input(f"\n{CYAN}Press Enter to return to main menu...{RESET}")


if __name__ == "__main__":
    controller = AppController()
    controller.start()
