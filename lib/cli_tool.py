"""Command-line task manager backed by in-memory User and Task objects."""

import argparse
import shlex

try:  # Support both `python -m lib.cli_tool` and `python lib/cli_tool.py`.
    from .models import Task, User
except ImportError:  # pragma: no cover - exercised by direct script execution
    from models import Task, User

# Users and their tasks live for as long as this CLI process is running.
users = {}


def add_task(args):
    """Find or create the named user, then add their new task."""
    user = users.get(args.user)
    if user is None:
        user = User(args.user)
        users[args.user] = user

    user.add_task(Task(args.title))


def complete_task(args):
    """Find a user's task and mark it complete, reporting missing records."""
    user = users.get(args.user)
    if user is None:
        print("❌ User not found.")
        return

    task = user.get_task_by_title(args.title)
    if task is None:
        print("❌ Task not found.")
        return

    task.complete()


def list_tasks(args):
    """Display all tasks belonging to a user and their current status."""
    user = users.get(args.user)
    if user is None:
        print("❌ User not found.")
        return
    if not user.tasks:
        print(f"{user.name} has no tasks.")
        return

    for task in user.tasks:
        marker = "✅" if task.completed else "⬜"
        print(f"{marker} {task.title}")


def _non_empty(value):
    """Reject blank names and titles at the command-line boundary."""
    if not value.strip():
        raise argparse.ArgumentTypeError("value cannot be empty")
    return value


def build_parser():
    """Build the root parser and its task-management subcommands."""
    parser = argparse.ArgumentParser(
        description="Manage tasks for users in the current process."
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="keep an in-memory session open for multiple commands",
    )
    subparsers = parser.add_subparsers(dest="command")

    add_parser = subparsers.add_parser(
        "add-task", aliases=["add"], help="add a task for a user"
    )
    add_parser.add_argument("user", type=_non_empty, help="user name")
    add_parser.add_argument("title", type=_non_empty, help="task title")
    add_parser.set_defaults(func=add_task)

    complete_parser = subparsers.add_parser(
        "complete-task", aliases=["complete"], help="complete a user's task"
    )
    complete_parser.add_argument("user", type=_non_empty, help="user name")
    complete_parser.add_argument("title", type=_non_empty, help="task title")
    complete_parser.set_defaults(func=complete_task)

    list_parser = subparsers.add_parser(
        "list-tasks", aliases=["list"], help="list a user's tasks"
    )
    list_parser.add_argument("user", type=_non_empty, help="user name")
    list_parser.set_defaults(func=list_tasks)
    return parser


def _run_interactive(parser):
    """Keep user/task objects alive while the user enters several commands."""
    print("Task manager ready. Enter a command, or 'quit' to exit.")
    while True:
        try:
            line = input("task-manager> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if line.lower() in {"quit", "exit"}:
            break
        if not line:
            continue

        try:
            args = parser.parse_args(shlex.split(line))
        except SystemExit:
            # Invalid interactive input should return to the prompt, not close the session.
            continue
        if not hasattr(args, "func"):
            parser.print_help()
            continue
        args.func(args)


def main(argv=None):
    """Parse a command and dispatch it to the matching operation."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.interactive:
        _run_interactive(parser)
    elif hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
