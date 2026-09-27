class Task:
    """A task with a title and a completion state."""

    def __init__(self, title):
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Task title must be a non-empty string.")
        self.title = title
        self.completed = False

    def complete(self):
        """Mark this task complete and give the user immediate feedback."""
        self.completed = True
        print(f"✅ Task '{self.title}' completed.")


class User:
    """An account that groups tasks and provides task lookup operations."""

    def __init__(self, name):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("User name must be a non-empty string.")
        self.name = name
        self.tasks = []

    def add_task(self, task):
        """Add a Task to this user and confirm the action."""
        if not isinstance(task, Task):
            raise TypeError("task must be a Task instance")
        self.tasks.append(task)
        print(f"📌 Task '{task.title}' added to {self.name}.")

    def get_task_by_title(self, title):
        """Return the first task with this title, or None when it is absent."""
        return next((task for task in self.tasks if task.title == title), None)
