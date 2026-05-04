"""Kanban board system for task management."""

import json
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


class TaskStatus(Enum):
    """Task status in kanban."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"


class TaskPriority(Enum):
    """Task priority level."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Task:
    """Individual task in kanban board."""

    id: str
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: str = ""
    due_date: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    tags: List[str] = None
    subtasks: List[str] = None
    comments: List[Dict[str, str]] = None

    def __post_init__(self):
        if self.created_at == "":
            self.created_at = datetime.now().isoformat()
        if self.updated_at == "":
            self.updated_at = datetime.now().isoformat()
        if self.tags is None:
            self.tags = []
        if self.subtasks is None:
            self.subtasks = []
        if self.comments is None:
            self.comments = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['status'] = self.status.value
        data['priority'] = self.priority.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create from dictionary."""
        data_copy = data.copy()
        data_copy['status'] = TaskStatus(data['status'])
        data_copy['priority'] = TaskPriority(data['priority'])
        return cls(**data_copy)


class KanbanBoard:
    """Kanban board for project task management."""

    def __init__(self, name: str = "Default Board"):
        self.name = name
        self.created_at = datetime.now().isoformat()
        self.tasks: Dict[str, Task] = {}
        self.task_order: Dict[TaskStatus, List[str]] = {
            status: [] for status in TaskStatus
        }

    def add_task(self, task: Task) -> Task:
        """Add task to board."""
        self.tasks[task.id] = task
        self.task_order[task.status].append(task.id)
        return task

    def create_task(self, task_id: str, title: str, description: str = "",
                   priority: TaskPriority = TaskPriority.MEDIUM) -> Task:
        """Create and add new task."""
        task = Task(
            id=task_id,
            title=title,
            description=description,
            priority=priority
        )
        return self.add_task(task)

    def remove_task(self, task_id: str) -> bool:
        """Remove task from board."""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        self.task_order[task.status].remove(task_id)
        del self.tasks[task_id]
        return True

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        return self.tasks.get(task_id)

    def move_task(self, task_id: str, new_status: TaskStatus) -> bool:
        """Move task to different status column."""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        old_status = task.status

        # Remove from old status
        self.task_order[old_status].remove(task_id)

        # Update task status
        task.status = new_status
        task.updated_at = datetime.now().isoformat()

        # Add to new status
        self.task_order[new_status].append(task_id)
        return True

    def reorder_task(self, task_id: str, new_position: int,
                     status: TaskStatus) -> bool:
        """Reorder task within status column."""
        if task_id not in self.task_order[status]:
            return False

        task_list = self.task_order[status]
        task_list.remove(task_id)
        task_list.insert(min(new_position, len(task_list)), task_id)
        return True

    def update_task(self, task_id: str, **kwargs) -> Optional[Task]:
        """Update task properties."""
        if task_id not in self.tasks:
            return None

        task = self.tasks[task_id]

        # Handle status changes specially
        if 'status' in kwargs:
            new_status = kwargs.pop('status')
            if isinstance(new_status, str):
                new_status = TaskStatus(new_status)
            self.move_task(task_id, new_status)

        # Update other fields
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)

        task.updated_at = datetime.now().isoformat()
        return task

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get all tasks with specific status."""
        task_ids = self.task_order[status]
        return [self.tasks[tid] for tid in task_ids if tid in self.tasks]

    def get_tasks_by_assignee(self, assignee: str) -> List[Task]:
        """Get all tasks assigned to person."""
        return [task for task in self.tasks.values() if task.assignee == assignee]

    def get_tasks_by_priority(self, priority: TaskPriority) -> List[Task]:
        """Get all tasks with specific priority."""
        return [task for task in self.tasks.values() if task.priority == priority]

    def get_overdue_tasks(self) -> List[Task]:
        """Get all overdue tasks."""
        now = datetime.now()
        overdue = []

        for task in self.tasks.values():
            if task.due_date:
                due = datetime.fromisoformat(task.due_date)
                if due < now and task.status != TaskStatus.DONE:
                    overdue.append(task)

        return sorted(overdue, key=lambda t: t.due_date)

    def add_comment(self, task_id: str, author: str, text: str) -> bool:
        """Add comment to task."""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        comment = {
            'author': author,
            'text': text,
            'timestamp': datetime.now().isoformat()
        }
        task.comments.append(comment)
        task.updated_at = datetime.now().isoformat()
        return True

    def add_subtask(self, task_id: str, subtask_id: str) -> bool:
        """Add subtask to task."""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        if subtask_id not in task.subtasks:
            task.subtasks.append(subtask_id)
            task.updated_at = datetime.now().isoformat()
            return True
        return False

    def get_board_stats(self) -> Dict[str, Any]:
        """Get board statistics."""
        stats = {
            'total_tasks': len(self.tasks),
            'tasks_by_status': {},
            'tasks_by_priority': {},
            'overdue_tasks': len(self.get_overdue_tasks()),
            'completion_rate': 0.0
        }

        # Count by status
        for status in TaskStatus:
            count = len(self.get_tasks_by_status(status))
            stats['tasks_by_status'][status.value] = count

        # Count by priority
        for priority in TaskPriority:
            count = len(self.get_tasks_by_priority(priority))
            stats['tasks_by_priority'][priority.name] = count

        # Calculate completion rate
        total = len(self.tasks)
        if total > 0:
            completed = len(self.get_tasks_by_status(TaskStatus.DONE))
            stats['completion_rate'] = (completed / total) * 100

        return stats

    def to_dict(self) -> Dict[str, Any]:
        """Convert board to dictionary."""
        return {
            'name': self.name,
            'created_at': self.created_at,
            'tasks': {tid: task.to_dict() for tid, task in self.tasks.items()},
            'task_order': {
                status.value: task_ids
                for status, task_ids in self.task_order.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KanbanBoard':
        """Create board from dictionary."""
        board = cls(data.get('name', 'Default Board'))
        board.created_at = data.get('created_at', datetime.now().isoformat())

        # Load tasks
        for task_id, task_data in data.get('tasks', {}).items():
            task = Task.from_dict(task_data)
            board.tasks[task_id] = task

        # Restore order
        for status_str, task_ids in data.get('task_order', {}).items():
            status = TaskStatus(status_str)
            board.task_order[status] = task_ids

        return board

    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'KanbanBoard':
        """Deserialize from JSON."""
        data = json.loads(json_str)
        return cls.from_dict(data)


class KanbanBoardManager:
    """Manages multiple kanban boards for project."""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.kanban_dir = self.project_path / ".kanban"
        self.kanban_dir.mkdir(parents=True, exist_ok=True)
        self.boards: Dict[str, KanbanBoard] = {}
        self._load_boards()

    def _load_boards(self) -> None:
        """Load all boards from disk."""
        for board_file in self.kanban_dir.glob("board_*.json"):
            try:
                with open(board_file, 'r') as f:
                    data = json.load(f)
                    board = KanbanBoard.from_dict(data)
                    board_id = board_file.stem.replace("board_", "")
                    self.boards[board_id] = board
            except (json.JSONDecodeError, OSError):
                pass

    def create_board(self, board_id: str, name: str) -> KanbanBoard:
        """Create new board."""
        board = KanbanBoard(name)
        self.boards[board_id] = board
        self.save_board(board_id)
        return board

    def get_board(self, board_id: str) -> Optional[KanbanBoard]:
        """Get board by ID."""
        return self.boards.get(board_id)

    def save_board(self, board_id: str) -> bool:
        """Save board to disk."""
        if board_id not in self.boards:
            return False

        board = self.boards[board_id]
        file_path = self.kanban_dir / f"board_{board_id}.json"

        try:
            with open(file_path, 'w') as f:
                f.write(board.to_json())
            return True
        except OSError:
            return False

    def save_all_boards(self) -> None:
        """Save all boards."""
        for board_id in self.boards:
            self.save_board(board_id)

    def delete_board(self, board_id: str) -> bool:
        """Delete board."""
        if board_id not in self.boards:
            return False

        del self.boards[board_id]
        file_path = self.kanban_dir / f"board_{board_id}.json"
        if file_path.exists():
            file_path.unlink()
        return True

    def list_boards(self) -> List[str]:
        """List all board IDs."""
        return list(self.boards.keys())
