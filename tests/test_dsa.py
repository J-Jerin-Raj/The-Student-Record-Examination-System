"""
Comprehensive Unit Tests for DSA Microproject.
Validates:
- CO1: Stack and Queue implementations
- CO2: Singly Linked List and Linear Search
- CO3: Searching and Sorting Algorithms
- Services: StudentManager (with Undo), ExamQueueManager, and WhatIfMarksSimulator
"""

import unittest
from structures.stack import Stack
from structures.queue import Queue
from structures.linked_list import SinglyLinkedList
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


class TestStack(unittest.TestCase):
    def test_push_pop_peek(self):
        s = Stack(capacity=3)
        self.assertTrue(s.is_empty())
        s.push(10)
        s.push(20)
        s.push(30)
        self.assertEqual(s.size(), 3)
        self.assertEqual(s.peek(), 30)

        with self.assertRaises(OverflowError):
            s.push(40)

        # LIFO check
        self.assertEqual(s.pop(), 30)
        self.assertEqual(s.pop(), 20)
        self.assertEqual(s.pop(), 10)
        self.assertTrue(s.is_empty())

        with self.assertRaises(IndexError):
            s.pop()


class TestQueue(unittest.TestCase):
    def test_enqueue_dequeue_peek(self):
        q = Queue(capacity=3)
        self.assertTrue(q.is_empty())
        q.enqueue("First")
        q.enqueue("Second")
        q.enqueue("Third")
        self.assertEqual(q.size(), 3)
        self.assertEqual(q.peek(), "First")

        with self.assertRaises(OverflowError):
            q.enqueue("Fourth")

        # FIFO check
        self.assertEqual(q.dequeue(), "First")
        self.assertEqual(q.dequeue(), "Second")
        self.assertEqual(q.dequeue(), "Third")
        self.assertTrue(q.is_empty())

        with self.assertRaises(IndexError):
            q.dequeue()


class TestSinglyLinkedList(unittest.TestCase):
    def test_linked_list_crud(self):
        ll = SinglyLinkedList()
        s1 = Student("STU01", "Alice", "CSE", 3, {"DSA": 80})
        s2 = Student("STU02", "Bob", "IT", 3, {"DSA": 90})
        s3 = Student("STU03", "Charlie", "ECE", 3, {"DSA": 70})

        # Insert at end
        ll.insert_at_end(s1)
        ll.insert_at_end(s2)
        # Insert at beginning
        ll.insert_at_beginning(s3)

        self.assertEqual(len(ll), 3)
        items = ll.to_list()
        self.assertEqual(items[0].student_id, "STU03")
        self.assertEqual(items[1].student_id, "STU01")
        self.assertEqual(items[2].student_id, "STU02")

        # Search by id
        found, comps = ll.search_by_id("STU01")
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Alice")
        self.assertEqual(comps, 2)

        # Update
        updated_s1 = Student("STU01", "Alice Updated", "CSE", 3, {"DSA": 95})
        success, old = ll.update_by_id("STU01", updated_s1)
        self.assertTrue(success)
        self.assertEqual(old.name, "Alice")

        # Delete
        deleted, _ = ll.delete_by_id("STU01")
        self.assertIsNotNone(deleted)
        self.assertEqual(deleted.name, "Alice Updated")
        self.assertEqual(len(ll), 2)


class TestStudentManagerAndUndo(unittest.TestCase):
    def test_undo_add_update_delete(self):
        sm = StudentManager()
        s1 = Student("STU01", "Alice", "CSE", 3, {"DSA": 85})

        # Test Add & Undo Add
        sm.add_student(s1)
        self.assertEqual(sm.count(), 1)
        self.assertIsNotNone(sm.get_student_by_id("STU01"))

        success, msg = sm.undo_last_action()
        self.assertTrue(success)
        self.assertEqual(sm.count(), 0)
        self.assertIsNone(sm.get_student_by_id("STU01"))

        # Test Update & Undo Update
        sm.add_student(s1)
        s1_modified = Student("STU01", "Alice Modified", "CSE", 3, {"DSA": 99})
        sm.update_student("STU01", s1_modified)
        self.assertEqual(sm.get_student_by_id("STU01").name, "Alice Modified")

        sm.undo_last_action()
        self.assertEqual(sm.get_student_by_id("STU01").name, "Alice")

        # Test Delete & Undo Delete
        sm.delete_student("STU01")
        self.assertEqual(sm.count(), 0)
        sm.undo_last_action()
        self.assertEqual(sm.count(), 1)
        self.assertEqual(sm.get_student_by_id("STU01").name, "Alice")


class TestExamQueueManager(unittest.TestCase):
    def test_exam_queue_workflow(self):
        eqm = ExamQueueManager()
        r1 = eqm.submit_request("STU01", "Alice", "Hall Ticket", "Session May 2026")
        r2 = eqm.submit_request("STU02", "Bob", "Re-evaluation", "DSA Paper 1")

        self.assertEqual(eqm.pending_count(), 2)
        self.assertEqual(eqm.peek_next().request_id, r1.request_id)

        # Dequeue in FIFO order
        p1, _ = eqm.process_next()
        self.assertEqual(p1.request_id, r1.request_id)
        self.assertEqual(eqm.pending_count(), 1)

        p2, _ = eqm.process_next()
        self.assertEqual(p2.request_id, r2.request_id)
        self.assertEqual(eqm.pending_count(), 0)


class TestAlgorithms(unittest.TestCase):
    def setUp(self):
        self.students = [
            Student("STU03", "Charlie", "ECE", 3, {"DSA": 70.0}),
            Student("STU01", "Alice", "CSE", 3, {"DSA": 90.0}),
            Student("STU04", "David", "MECH", 3, {"DSA": 60.0}),
            Student("STU02", "Bob", "IT", 3, {"DSA": 85.0}),
        ]

    def test_searching(self):
        # Linear search
        res_linear = linear_search_list(self.students, "STU02")
        self.assertTrue(res_linear.found)
        self.assertEqual(res_linear.data.name, "Bob")

        # Binary search on sorted array
        sorted_by_id = sorted(self.students, key=lambda s: s.student_id)
        res_bin = binary_search(sorted_by_id, "STU02")
        self.assertTrue(res_bin.found)
        self.assertEqual(res_bin.data.name, "Bob")

    def test_sorting_algorithms(self):
        # Sort by marks descending (Merit list)
        res_bubble = bubble_sort(self.students, criterion="marks", reverse=True)
        res_insert = insertion_sort(self.students, criterion="marks", reverse=True)
        res_merge = merge_sort(self.students, criterion="marks", reverse=True)

        expected_order = ["Alice", "Bob", "Charlie", "David"]
        self.assertEqual([s.name for s in res_bubble.sorted_items], expected_order)
        self.assertEqual([s.name for s in res_insert.sorted_items], expected_order)
        self.assertEqual([s.name for s in res_merge.sorted_items], expected_order)


class TestWhatIfSimulator(unittest.TestCase):
    def test_simulator_diagnostics_and_goal(self):
        s = Student(
            "STU01",
            "Test Student",
            "CSE",
            3,
            {"DSA": 85.0, "WebDev": 65.0, "Maths": 45.0, "OS": 75.0},
        )
        # Current average = (85+65+45+75)/4 = 67.5%
        self.assertEqual(s.percentage, 67.5)

        diagnoses = WhatIfMarksSimulator.diagnose_student(s)
        self.assertEqual(len(diagnoses), 4)
        # Maths should be critical (<50) and top improvement headroom
        self.assertEqual(diagnoses[0].subject, "Maths")
        self.assertEqual(diagnoses[0].status, "Critical")

        # Goal Analysis for 80% (Achievable)
        goal_res = WhatIfMarksSimulator.analyze_goal(s, target_percentage=80.0)
        self.assertTrue(goal_res.is_achievable)
        self.assertGreater(goal_res.required_overall_increase, 0)

        # Goal Analysis for 105% (Impossible)
        unachievable_res = WhatIfMarksSimulator.analyze_goal(s, target_percentage=105.0)
        self.assertFalse(unachievable_res.is_achievable)


if __name__ == "__main__":
    unittest.main()
