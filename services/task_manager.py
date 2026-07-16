"""
This module implements the TaskManager service class.
"""

import json
import os
from typing import List, Optional, Generator
from pydantic import ValidationError
from models.task import Task
from utils.decorators import log_action
from utils.logger import get_logger

logger = get_logger("task_manager")

class TaskManager:
    """
    Manages task CRUD operations, persistence, and statistics.
    """
    def __init__(self, file_path: Optional[str] = None):
        """
        Initializes TaskManager with memory storage and persistence settings.
        
        Args:
            file_path (Optional[str]): Path to JSON file for persistence.
        """
        if file_path is None:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
            os.makedirs(base_dir, exist_ok=True)
            file_path = os.path.join(base_dir, "tasks.json")
            
        self.file_path = file_path
        self.tasks: List[Task] = []
        self.load_tasks()

    def iter_tasks(self) -> Generator[Task, None, None]:
        """
        Generator to iterate over the task list.
        
        Yields:
            Task: The next task object in memory.
        """
        for task in self.tasks:
            yield task

    @log_action
    def load_tasks(self) -> None:
        """
        Loads tasks from the JSON file into memory. Handles missing or corrupt files gracefully.
        """
        if not os.path.exists(self.file_path):
            self.tasks = []
            return
            
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    self.tasks = []
                    return
                data = json.loads(content)
                self.tasks = [Task.model_validate(item) for item in data]
        except Exception as e:
            logger.error(f"Failed to load tasks from {self.file_path}: {e}")
            self.tasks = []

    @log_action
    def save_tasks(self) -> None:
        """
        Saves current tasks from memory to the JSON file atomically.
        """
        temp_path = self.file_path + ".tmp"
        try:
            # Pydantic v2 dump compatibility (mode="json")
            data = [task.model_dump(mode="json") for task in self.iter_tasks()]
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            # Atomic replacement
            if os.path.exists(self.file_path):
                os.remove(self.file_path)
            os.rename(temp_path, self.file_path)
        except Exception as e:
            logger.error(f"Failed to save tasks to {self.file_path}: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e

    @log_action
    def add_task(self, title: str, description: str = "", priority: str = "Medium") -> Task:
        """
        Creates and saves a new task.
        
        Args:
            title (str): Task title.
            description (str): Task description.
            priority (str): Task priority (Low, Medium, High).
            
        Returns:
            Task: The newly created task.
        """
        next_id = max((t.id for t in self.iter_tasks()), default=0) + 1
        try:
            task = Task(
                id=next_id,
                title=title,
                description=description,
                priority=priority,
                completed=False
            )
        except ValidationError as ve:
            logger.error(f"Validation Failed: {str(ve)}")
            raise ve
            
        self.tasks.append(task)
        self.save_tasks()
        logger.info(f"Task Created: {task.id} - {task.title}")
        return task

    @log_action
    def view_tasks(self) -> List[Task]:
        """
        Returns a copy of all tasks in memory.
        
        Returns:
            List[Task]: A list containing all tasks.
        """
        return list(self.iter_tasks())


    @log_action
    def complete_task(self, task_id: int) -> Optional[Task]:
        """
        Marks a task as completed.
        
        Args:
            task_id (int): ID of the task to complete.
            
        Returns:
            Optional[Task]: The completed task, or None if not found.
        """
        task = next((t for t in self.iter_tasks() if t.id == task_id), None)
        if task:
            task.completed = True
            self.save_tasks()
            logger.info(f"Task Completed: {task.id} - {task.title}")
            return task
        return None

    @log_action
    def delete_task(self, task_id: int) -> bool:
        """
        Deletes a task by ID.
        
        Args:
            task_id (int): ID of the task to delete.
            
        Returns:
            bool: True if task was deleted, False otherwise.
        """
        task_to_delete = next((t for t in self.iter_tasks() if t.id == task_id), None)
        if task_to_delete:
            self.tasks.remove(task_to_delete)
            self.save_tasks()
            logger.info(f"Task Deleted: {task_id}")
            return True
        return False

    @log_action
    def search_tasks(self, query: str) -> List[Task]:
        """
        Searches tasks by title or description.
        
        Args:
            query (str): Search query.
            
        Returns:
            List[Task]: Matching tasks.
        """
        query_lower = query.lower()
        return [
            task for task in self.iter_tasks()
            if query_lower in task.title.lower() or (task.description and query_lower in task.description.lower())
        ]

    @log_action
    def update_task(self, task_id: int, title: Optional[str] = None, description: Optional[str] = None, priority: Optional[str] = None) -> Optional[Task]:
        """
        Updates task fields.
        
        Args:
            task_id (int): ID of the task to update.
            title (Optional[str]): New title.
            description (Optional[str]): New description.
            priority (Optional[str]): New priority.
            
        Returns:
            Optional[Task]: The updated task, or None if not found.
        """
        task = next((t for t in self.iter_tasks() if t.id == task_id), None)
        if task:
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if priority is not None:
                task.priority = priority
            self.save_tasks()
            return task
        return None

    @log_action
    def show_statistics(self) -> dict:
        """
        Calculates and returns statistics of the tasks.
        
        Returns:
            dict: Task statistics.
        """
        total = self.get_total_tasks()
        completed = self.get_completed_tasks_count()
        pending = self.get_pending_tasks_count()
        percentage = (completed / total * 100) if total > 0 else 0.0
        
        priorities = {
            "Low": self.get_low_priority_count(),
            "Medium": self.get_medium_priority_count(),
            "High": self.get_high_priority_count()
        }
        
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "percentage_completed": round(percentage, 2),
            "priority_counts": priorities
        }

    def get_total_tasks(self) -> int:
        """Exposes the total tasks count."""
        return len(self.tasks)
        
    def get_completed_tasks_count(self) -> int:
        """Exposes completed tasks count."""
        return sum(1 for t in self.iter_tasks() if t.completed)
        
    def get_pending_tasks_count(self) -> int:
        """Exposes pending tasks count."""
        return self.get_total_tasks() - self.get_completed_tasks_count()
        
    def get_high_priority_count(self) -> int:
        """Exposes high priority tasks count."""
        return sum(1 for t in self.iter_tasks() if t.priority == "High")
        
    def get_medium_priority_count(self) -> int:
        """Exposes medium priority tasks count."""
        return sum(1 for t in self.iter_tasks() if t.priority == "Medium")
        
    def get_low_priority_count(self) -> int:
        """Exposes low priority tasks count."""
        return sum(1 for t in self.iter_tasks() if t.priority == "Low")

    @log_action
    def filter_tasks(self, status: Optional[str] = None, priority: Optional[str] = None) -> List[Task]:
        """
        Filters tasks by completion status and/or priority rating.
        
        Args:
            status (Optional[str]): Status filter ('All', 'Pending', 'Completed').
            priority (Optional[str]): Priority filter ('All', 'High', 'Medium', 'Low').
            
        Returns:
            List[Task]: Filtered tasks.
        """
        tasks = self.view_tasks()
        if status == "Completed":
            tasks = [t for t in tasks if t.completed]
        elif status == "Pending":
            tasks = [t for t in tasks if not t.completed]
            
        if priority is not None and priority != "All":
            tasks = [t for t in tasks if t.priority == priority]
            
        return tasks

    @log_action
    def sort_tasks(self, tasks: List[Task], criterion: str) -> List[Task]:
        """
        Sorts the given tasks list based on sorting criteria.
        
        Args:
            tasks (List[Task]): Tasks list.
            criterion (str): Sort criterion.
            
        Returns:
            List[Task]: Sorted tasks.
        """
        prio_map = {"High": 3, "Medium": 2, "Low": 1}
        if criterion == "Newest First":
            return sorted(tasks, key=lambda t: t.created_at, reverse=True)
        elif criterion == "Oldest First":
            return sorted(tasks, key=lambda t: t.created_at)
        elif criterion == "High Priority First":
            return sorted(tasks, key=lambda t: prio_map.get(t.priority, 0), reverse=True)
        elif criterion == "Low Priority First":
            return sorted(tasks, key=lambda t: prio_map.get(t.priority, 0))
        return tasks


