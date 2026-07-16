import unittest
import os
import tempfile
from services.task_manager import TaskManager
from models.task import Task

class TestTaskManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary file path for tasks.json to isolate tests
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_file_path = os.path.join(self.temp_dir.name, "test_tasks.json")
        self.manager = TaskManager(file_path=self.temp_file_path)

    def tearDown(self):
        # Clean up temporary directory and files
        self.temp_dir.cleanup()

    def test_add_task(self):
        task = self.manager.add_task(title="Test Task", description="Test Description", priority="High")
        self.assertEqual(task.id, 1)
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.description, "Test Description")
        self.assertEqual(task.priority, "High")
        self.assertFalse(task.completed)
        self.assertEqual(len(self.manager.view_tasks()), 1)

    def test_add_task_invalid_title(self):
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            self.manager.add_task(title="Ab")

    def test_add_multiple_tasks_incrementing_ids(self):
        task1 = self.manager.add_task("Task 1")
        task2 = self.manager.add_task("Task 2")
        self.assertEqual(task1.id, 1)
        self.assertEqual(task2.id, 2)

    def test_delete_task(self):
        task = self.manager.add_task("To Delete")
        success = self.manager.delete_task(task.id)
        self.assertTrue(success)
        self.assertEqual(len(self.manager.view_tasks()), 0)

    def test_delete_non_existent_task(self):
        success = self.manager.delete_task(999)
        self.assertFalse(success)

    def test_update_task(self):
        task = self.manager.add_task("Original Title", "Original Desc", "Low")
        updated = self.manager.update_task(
            task.id, 
            title="Updated Title", 
            description="Updated Desc", 
            priority="High"
        )
        self.assertIsNotNone(updated)
        self.assertEqual(updated.title, "Updated Title")
        self.assertEqual(updated.description, "Updated Desc")
        self.assertEqual(updated.priority, "High")

        # Verify update persists
        refetched_task = self.manager.view_tasks()[0]
        self.assertEqual(refetched_task.title, "Updated Title")

    def test_complete_task(self):
        task = self.manager.add_task("Task")
        self.assertFalse(task.completed)
        completed_task = self.manager.complete_task(task.id)
        self.assertIsNotNone(completed_task)
        self.assertTrue(completed_task.completed)

    def test_search_tasks(self):
        self.manager.add_task("Apple", "Buy fresh fruit")
        self.manager.add_task("Banana", "Yellow fruit")
        self.manager.add_task("Shopping", "Buy groceries")

        results1 = self.manager.search_tasks("fruit")
        self.assertEqual(len(results1), 2)  # Apple and Banana

        results2 = self.manager.search_tasks("Buy")
        self.assertEqual(len(results2), 2)  # Apple and Shopping

    def test_show_statistics(self):
        self.manager.add_task("Task 1", priority="High")
        self.manager.add_task("Task 2", priority="Medium")
        t3 = self.manager.add_task("Task 3", priority="Low")
        self.manager.complete_task(t3.id)

        stats = self.manager.show_statistics()
        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["completed"], 1)
        self.assertEqual(stats["pending"], 2)
        self.assertEqual(stats["percentage_completed"], 33.33)
        self.assertEqual(stats["priority_counts"]["High"], 1)
        self.assertEqual(stats["priority_counts"]["Medium"], 1)
        self.assertEqual(stats["priority_counts"]["Low"], 1)

    def test_task_manager_new_methods(self):
        t1 = self.manager.add_task("First Task", "Description 1", "Low")
        t2 = self.manager.add_task("Second Task", "Description 2", "High")
        
        # Test view_tasks
        tasks = self.manager.view_tasks()
        self.assertEqual(len(tasks), 2)
        
        # Test iter_tasks generator
        task_list_from_generator = list(self.manager.iter_tasks())
        self.assertEqual(len(task_list_from_generator), 2)
        self.assertEqual(task_list_from_generator[0].title, "First Task")
        
        # Test search_tasks
        search_results = self.manager.search_tasks("Second")
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0].id, t2.id)

        # Test show_statistics
        stats = self.manager.show_statistics()
        self.assertEqual(stats["total"], 2)
        self.assertEqual(stats["priority_counts"]["High"], 1)

    def test_filter_tasks(self):
        t1 = self.manager.add_task("Task A", priority="High")
        t2 = self.manager.add_task("Task B", priority="Low")
        t3 = self.manager.add_task("Task C", priority="High")
        self.manager.complete_task(t1.id)

        # Filter completed
        comp = self.manager.filter_tasks(status="Completed")
        self.assertEqual(len(comp), 1)
        self.assertEqual(comp[0].title, "Task A")

        # Filter pending
        pend = self.manager.filter_tasks(status="Pending")
        self.assertEqual(len(pend), 2)

        # Filter priority High
        prio_high = self.manager.filter_tasks(priority="High")
        self.assertEqual(len(prio_high), 2)

        # Filter combination (completed + High)
        combo = self.manager.filter_tasks(status="Completed", priority="High")
        self.assertEqual(len(combo), 1)

    def test_sort_tasks(self):
        t1 = self.manager.add_task("Task A", priority="Low")
        t2 = self.manager.add_task("Task B", priority="High")
        t3 = self.manager.add_task("Task C", priority="Medium")

        # High priority first
        high_prio = self.manager.sort_tasks(self.manager.view_tasks(), "High Priority First")
        self.assertEqual(high_prio[0].title, "Task B")
        self.assertEqual(high_prio[1].title, "Task C")
        self.assertEqual(high_prio[2].title, "Task A")

        # Low priority first
        low_prio = self.manager.sort_tasks(self.manager.view_tasks(), "Low Priority First")
        self.assertEqual(low_prio[0].title, "Task A")
        self.assertEqual(low_prio[1].title, "Task C")
        self.assertEqual(low_prio[2].title, "Task B")

    def test_individual_statistics(self):
        self.manager.add_task("Task 1", priority="High")
        self.manager.add_task("Task 2", priority="Medium")
        t3 = self.manager.add_task("Task 3", priority="Low")
        self.manager.complete_task(t3.id)

        self.assertEqual(self.manager.get_total_tasks(), 3)
        self.assertEqual(self.manager.get_completed_tasks_count(), 1)
        self.assertEqual(self.manager.get_pending_tasks_count(), 2)
        self.assertEqual(self.manager.get_high_priority_count(), 1)
        self.assertEqual(self.manager.get_medium_priority_count(), 1)
        self.assertEqual(self.manager.get_low_priority_count(), 1)

if __name__ == '__main__':
    unittest.main()
