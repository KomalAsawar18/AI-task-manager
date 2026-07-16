"""
This module implements the Command Line Interface (CLI) for the AI Task Manager.
"""

import sys
from services.task_manager import TaskManager
from utils.helpers import format_table, get_non_empty_input, get_choice_input, get_int_input
from utils.logger import get_logger

logger = get_logger("main")

def print_menu() -> None:
    """
    Displays the interactive CLI main menu.
    """
    print("\n" + "=" * 40)
    print("        ★  AI TASK MANAGER (MVP)  ★")
    print("=" * 40)
    print("  1. Add Task")
    print("  2. View Tasks")
    print("  3. Complete Task")
    print("  4. Delete Task")
    print("  5. Search Task")
    print("  6. Statistics")
    print("  7. Exit")
    print("=" * 40)

def display_tasks(tasks, title_msg: str = "All Tasks") -> None:
    """
    Neatly formats and prints a list of tasks in an ASCII table.
    """
    if not tasks:
        print("\n--- No tasks found. ---")
        return
        
    print(f"\n--- {title_msg} ---")
    headers = ["ID", "Title", "Description", "Priority", "Status", "Created At"]
    rows = []
    for t in tasks:
        status_str = "✓ Completed" if t.completed else "Pending"
        # Format created_at to be cleaner: e.g., 2026-07-16 00:19
        clean_date = t.created_at.strftime("%Y-%m-%d %H:%M")
        desc = t.description if t.description else ""
        rows.append([t.id, t.title, desc, t.priority, status_str, clean_date])
        
    print(format_table(headers, rows))

def handle_add_task(manager: TaskManager) -> None:
    """
    Guides the user to add a new task.
    """
    print("\n--- Add New Task ---")
    title = get_non_empty_input("Enter Title (min 3 chars): ")
    while len(title) < 3:
        print("Error: Title must be at least 3 characters long.")
        title = get_non_empty_input("Enter Title (min 3 chars): ")
        
    description = input("Enter Description (optional): ").strip()
    priority = get_choice_input("Enter Priority", ["Low", "Medium", "High"])
    
    try:
        task = manager.add_task(title, description, priority)
        print(f"\nSuccess: Task '{task.title}' added with ID {task.id}!")
    except Exception as e:
        logger.error(f"Error while adding task: {e}")
        print(f"Error: Could not add task. {e}")

def handle_view_tasks(manager: TaskManager) -> None:
    """
    Displays all tasks.
    """
    tasks = manager.view_tasks()
    display_tasks(tasks)

def handle_complete_task(manager: TaskManager) -> None:
    """
    Guides the user to mark a task as completed.
    """
    print("\n--- Complete Task ---")
    task_id = get_int_input("Enter Task ID to complete: ")
    
    try:
        task = manager.complete_task(task_id)
        if task:
            print(f"\nSuccess: Task '{task.title}' marked as completed!")
        else:
            print(f"Error: Task with ID {task_id} not found.")
    except Exception as e:
        logger.error(f"Error while completing task: {e}")
        print(f"Error: Could not complete task. {e}")

def handle_delete_task(manager: TaskManager) -> None:
    """
    Guides the user to delete a task.
    """
    print("\n--- Delete Task ---")
    task_id = get_int_input("Enter Task ID to delete: ")
    
    try:
        success = manager.delete_task(task_id)
        if success:
            print(f"\nSuccess: Task with ID {task_id} deleted successfully!")
        else:
            print(f"Error: Task with ID {task_id} not found.")
    except Exception as e:
        logger.error(f"Error while deleting task: {e}")
        print(f"Error: Could not delete task. {e}")

def handle_search_task(manager: TaskManager) -> None:
    """
    Guides the user to search for tasks.
    """
    print("\n--- Search Tasks ---")
    query = get_non_empty_input("Enter search query: ")
    
    try:
        results = manager.search_task(query)
        display_tasks(results, f"Search Results for '{query}'")
    except Exception as e:
        logger.error(f"Error while searching tasks: {e}")
        print(f"Error: Search failed. {e}")

def handle_statistics(manager: TaskManager) -> None:
    """
    Displays task execution metrics.
    """
    print("\n--- Statistics ---")
    try:
        stats = manager.show_statistics()
        print(f"  Total Tasks:          {stats['total']}")
        print(f"  Completed Tasks:      {stats['completed']}")
        print(f"  Pending Tasks:        {stats['pending']}")
        print(f"  Completion Rate:      {stats['percentage_completed']}%")
        print("  Tasks by Priority:")
        for prio, count in stats['priority_counts'].items():
            print(f"    - {prio}: {count}")
    except Exception as e:
        logger.error(f"Error retrieving statistics: {e}")
        print(f"Error: Could not load statistics. {e}")

def main() -> None:
    """
    Main entry point for the CLI program.
    """
    manager = TaskManager()
    logger.info("CLI Application started.")
    
    while True:
        try:
            print_menu()
            choice = input("Enter choice (1-7): ").strip()
            
            if choice == "1":
                handle_add_task(manager)
            elif choice == "2":
                handle_view_tasks(manager)
            elif choice == "3":
                handle_complete_task(manager)
            elif choice == "4":
                handle_delete_task(manager)
            elif choice == "5":
                handle_search_task(manager)
            elif choice == "6":
                handle_statistics(manager)
            elif choice == "7":
                print("\nSaving data and exiting...")
                manager.save_tasks()
                print("Thank you for using AI Task Manager. Goodbye!")
                logger.info("Application exited by user choice.")
                break
            else:
                print("Error: Invalid option. Please enter a number between 1 and 7.")
        except KeyboardInterrupt:
            print("\n\nSaving data and exiting...")
            try:
                manager.save_tasks()
            except Exception as e:
                logger.error(f"Failed to save tasks on interrupt: {e}")
            print("Application interrupted. Goodbye!")
            logger.info("Application interrupted.")
            break
        except Exception as e:
            logger.error(f"Unexpected error in CLI loop: {e}", exc_info=True)
            print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
