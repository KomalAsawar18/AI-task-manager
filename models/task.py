"""
This module defines the Task data model.
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field

class Task(BaseModel):
    """
    Represents a task in the AI Task Manager application.
    
    Attributes:
        id (int): A positive integer unique identifier.
        title (str): Title of the task (minimum 3 characters).
        description (Optional[str]): Optional detailed description.
        priority (Literal["Low", "Medium", "High"]): The severity/urgency of the task.
        completed (bool): Completion status, defaults to False.
        created_at (datetime): Automatic ISO timestamp of creation.
    """
    id: int = Field(..., gt=0, description="A positive integer unique identifier for the task.")
    title: str = Field(..., min_length=3, description="Title of the task (minimum 3 characters).")
    description: Optional[str] = Field(default=None, description="Optional detailed description of the task.")
    priority: Literal["Low", "Medium", "High"] = Field(default="Medium", description="Task priority (Low, Medium, High).")
    completed: bool = Field(default=False, description="Completion status of the task.")
    created_at: datetime = Field(default_factory=datetime.now, description="Automatic timestamp when task was created.")
