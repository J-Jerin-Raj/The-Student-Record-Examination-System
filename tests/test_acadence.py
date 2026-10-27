"""
Automated Unit Test Suite for Acadence - Student Academic & Examination Assistant.
Rigorously tests:
- CO1: Custom Stack and Queue
- CO2: Singly Linked List and Linear Search
- CO3: Searching and Sorting Algorithms (with edge cases: duplicates, empty, reverse)
- Priority Engine & Rationale Generation
- Exam Schedule Conflict Detection
- Academic Planner Multi-Level Undo Engine
- Target Score Calculator & Performance Analyzer
"""

import unittest
import os
from datetime import datetime, timedelta

from data_structures.stack import Stack
from data_structures.queue import Queue
from data_structures.linked_list import SinglyLinkedList
from algorithms.searching import linear_search, binary_search
from algorithms.sorting import bubble_sort, insertion_sort, merge_sort
from models import Task, Exam, Assessment
import database as db
from services.priority_engine import PriorityEngine
from services.academic_planner import AcademicPlannerService
from services.exam_manager import ExamManagerService
from services.performance_analyzer import PerformanceAnalyzerService
from services.rescue_mode import AcademicRescueService


class TestStack(unittest.TestCase):
    def test_lifo_operations(self):
        s = Stack(capacity=4)
        self.assertTrue(s.is_empty())
        self.assertEqual(s.size(), 0)

        s.push("Action 1")
        s.push("Action 2")
        s.push("Action 3")

        self.assertEqual(s.size(), 3)
        self.assertEqual(s.peek(), "Action 3")

        # LIFO check
        self.assertEqual(s.pop(), "Action 3")
        self.assertEqual(s.pop(), "Action 2")
        self.assertEqual(s.pop(), "Action 1")
        self.assertTrue(s.is_empty())

        with self.assertRaises(IndexError):
            s.pop()


class TestQueue(unittest.TestCase):
    def test_fifo_operations(self):
        q = Queue(capacity=3)
        self.assertTrue(q.is_empty())
        self.assertEqual(q.size(), 0)

        q.enqueue("Req 1")
        q.enqueue("Req 2")
        q.enqueue("Req 3")

        self.assertEqual(q.size(), 3)
        self.assertEqual(q.front(), "Req 1")

        with self.assertRaises(OverflowError):
            q.enqueue("Req 4")

        # FIFO check
        self.assertEqual(q.dequeue(), "Req 1")
        self.assertEqual(q.dequeue(), "Req 2")
        self.assertEqual(q.dequeue(), "Req 3")
        self.assertTrue(q.is_empty())

        with self.assertRaises(IndexError):
            q.dequeue()


class TestSinglyLinkedList(unittest.TestCase):
    def test_crud_and_traversal(self):
        ll = SinglyLinkedList()
        self.assertTrue(ll.is_empty())

        t1 = {"id": 101, "title": "Maths Assignment"}
        t2 = {"id": 102, "title": "DSA Lab"}
        t3 = {"id": 103, "title": "OS Project"}

        # Insert at front & rear
        ll.insert_rear(t1)
        ll.insert_rear(t2)
        ll.insert_front(t3)  # t3 becomes head

        self.assertEqual(len(ll), 3)
        items = ll.to_list()
        self.assertEqual(items[0]["id"], 103)
        self.assertEqual(items[1]["id"], 101)
        self.assertEqual(items[2]["id"], 102)

        # Search by id
        found, comps = ll.search_by_id("101")
        self.assertIsNotNone(found)
        self.assertEqual(found["title"], "Maths Assignment")
        self.assertEqual(comps, 2)

        # Update by id
        updated_t1 = {"id": 101, "title": "Maths Assignment Updated"}
        ok, old = ll.update_by_id("101", updated_t1)
        self.assertTrue(ok)
        self.assertEqual(old["title"], "Maths Assignment")

        # Delete by id
        del_item, del_comps = ll.delete_by_id("101")
        self.assertIsNotNone(del_item)
        self.assertEqual(del_item["title"], "Maths Assignment Updated")
        self.assertEqual(len(ll), 2)


class TestAlgorithms(unittest.TestCase):
    def test_searching(self):
        arr = [42, 17, 89, 5, 23, 67, 31]
        target = 23

        # Linear Search on unsorted array
        res_linear = linear_search(arr, target)
        self.assertTrue(res_linear.found)
        self.assertEqual(res_linear.data, 23)
        self.assertEqual(res_linear.index, 4)

        # Binary Search on sorted array
        sorted_arr = sorted(arr)  # [5, 17, 23, 31, 42, 67, 89]
        res_bin = binary_search(sorted_arr, target)
        self.assertTrue(res_bin.found)
        self.assertEqual(res_bin.data, 23)
        self.assertEqual(res_bin.index, 2)
        self.assertLessEqual(res_bin.comparisons, 4)

        # Search for non-existent target
        res_absent = binary_search(sorted_arr, 999)
        self.assertFalse(res_absent.found)

    def test_sorting(self):
        datasets = [
            [45, 12, 89, 3, 21, 67, 12],  # with duplicate
            [],                           # empty
            [99],                         # single item
            [1, 2, 3, 4, 5],              # already sorted
            [5, 4, 3, 2, 1],              # reverse sorted
        ]

        for d in datasets:
            expected = sorted(d)
            expected_rev = sorted(d, reverse=True)

            res_b = bubble_sort(d)
            self.assertEqual(res_b.sorted_items, expected)

            res_i = insertion_sort(d)
            self.assertEqual(res_i.sorted_items, expected)

            res_m = merge_sort(d)
            self.assertEqual(res_m.sorted_items, expected)

            # Test reverse order
            res_m_rev = merge_sort(d, reverse=True)
            self.assertEqual(res_m_rev.sorted_items, expected_rev)


class TestPriorityEngine(unittest.TestCase):
    def test_urgency_and_vulnerability(self):
        now = datetime.now()
        # Overdue task
        t_overdue = Task(
            id=1,
            title="Overdue Report",
            subject="Operating Systems",
            deadline=(now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"),
            priority="Critical",
            estimated_effort=2.0,
        )
        b_overdue = PriorityEngine.evaluate_task(t_overdue, {"Operating Systems": 45.0}, warning_threshold=60.0)
        self.assertTrue(b_overdue.is_overdue)
        self.assertGreater(b_overdue.urgency_score, 100.0)
        self.assertGreater(b_overdue.subject_vulnerability_score, 0.0)

        # Non-urgent task in good subject
        t_future = Task(
            id=2,
            title="Future Essay",
            subject="Web Development",
            deadline=(now + timedelta(days=14)).strftime("%Y-%m-%d %H:%M"),
            priority="Low",
            estimated_effort=5.0,
        )
        b_future = PriorityEngine.evaluate_task(t_future, {"Web Development": 88.0}, warning_threshold=60.0)
        self.assertFalse(b_future.is_overdue)
        self.assertLess(b_future.total_score, b_overdue.total_score)


class TestExamConflictDetector(unittest.TestCase):
    def setUp(self):
        db.init_db()
        db.clear_all_data()

    def test_conflict_detection(self):
        em = ExamManagerService()

        # Exam 1: 09:30 - 12:30 on 2026-11-15
        e1 = Exam(
            subject="Data Structures",
            exam_date="2026-11-15",
            start_time="09:30",
            end_time="12:30",
            venue="Hall 1",
            priority="High",
        )
        em.add_exam(e1)

        # Exam 2: 11:00 - 14:00 on 2026-11-15 (Overlaps with Exam 1!)
        e2 = Exam(
            subject="Operating Systems",
            exam_date="2026-11-15",
            start_time="11:00",
            end_time="14:00",
            venue="Hall 2",
            priority="Critical",
        )
        ok, msg, _ = em.add_exam(e2)
        self.assertTrue(ok)
        self.assertIn("Warning: A schedule clash was detected", msg)

        conflicts = em.detect_conflicts()
        self.assertEqual(len(conflicts), 1)
        self.assertIn("Data Structures", conflicts[0]["clashing_subjects"])
        self.assertIn("Operating Systems", conflicts[0]["clashing_subjects"])


class TestAcademicPlannerUndo(unittest.TestCase):
    def setUp(self):
        db.init_db()
        db.clear_all_data()

    def test_undo_stack_operations(self):
        planner = AcademicPlannerService()
        now = datetime.now()

        t = Task(
            title="Undo Test Task",
            subject="Algorithms",
            deadline=(now + timedelta(days=2)).strftime("%Y-%m-%d %H:%M"),
            priority="High",
            status="Pending",
        )

        # 1. Add Task and Undo Add
        ok, _, tid = planner.add_task(t)
        self.assertTrue(ok)
        self.assertIsNotNone(db.get_task_by_id(tid))

        # Undo addition
        undo_ok, undo_msg = planner.undo_last_action()
        self.assertTrue(undo_ok)
        self.assertIsNone(db.get_task_by_id(tid))

        # 2. Add Task, Update, and Undo Update
        _, _, tid2 = planner.add_task(t)
        t_loaded = db.get_task_by_id(tid2)
        t_loaded.title = "Modified Title"
        planner.update_task(t_loaded)
        self.assertEqual(db.get_task_by_id(tid2).title, "Modified Title")

        planner.undo_last_action()
        self.assertEqual(db.get_task_by_id(tid2).title, "Undo Test Task")


class TestPerformanceAnalyzer(unittest.TestCase):
    def test_target_score_calculator(self):
        # Student has current average of 70%, wants 80% on next 100-mark exam with 30% weight
        res = PerformanceAnalyzerService.calculate_required_score(
            subject="Algorithms",
            target_average=80.0,
            upcoming_max_marks=100.0,
            upcoming_weightage=30.0,
        )
        self.assertIsNotNone(res["required_marks"])
        self.assertTrue(res["is_achievable"])


if __name__ == "__main__":
    unittest.main()
