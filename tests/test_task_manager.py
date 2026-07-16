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
        self.assertEqual(len(self.manager.get_tasks()), 1)

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
        self.assertEqual(len(self.manager.get_tasks()), 0)

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
        refetched_task = self.manager.get_tasks()[0]
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

    def test_get_statistics(self):
        self.manager.add_task("Task 1", priority="High")
        self.manager.add_task("Task 2", priority="Medium")
        t3 = self.manager.add_task("Task 3", priority="Low")
        self.manager.complete_task(t3.id)

        stats = self.manager.get_statistics()
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
        
        # Test search_task
        search_results = self.manager.search_task("Second")
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0].id, t2.id)
        
        # Test show_statistics
        stats = self.manager.show_statistics()
        self.assertEqual(stats["total"], 2)
        self.assertEqual(stats["priority_counts"]["High"], 1)

if __name__ == '__main__':
    unittest.main()
