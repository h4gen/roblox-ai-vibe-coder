import json
import os
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict

@dataclass
class TodoItem:
    task: str
    status: str = "pending"  # pending, active, completed

@dataclass
class PlanState:
    goal: str
    todos: List[TodoItem]
    notes: List[str]

class PlanManager:
    def __init__(self):
        self.state: Optional[PlanState] = None

    def create_plan(self, goal: str, todos: List[str]):
        """Creates a new plan, overwriting any existing one."""
        self.state = PlanState(
            goal=goal,
            todos=[TodoItem(task=t) for t in todos],
            notes=[]
        )
        return f"Plan created: {goal} with {len(todos)} steps."

    def update_todo(self, index: int, status: str):
        """Updates the status of a todo item."""
        if not self.state or not self.state.todos:
            return "No active plan."
        
        if 0 <= index < len(self.state.todos):
            self.state.todos[index].status = status
            return f"Updated step {index+1} to '{status}'."
        return f"Invalid step index {index}."

    def add_note(self, note: str):
        """Adds a note to the plan."""
        if not self.state:
            return "No active plan to add notes to."
        self.state.notes.append(note)
        return "Note added."

    def clear_plan(self):
        """Clears the current plan."""
        self.state = None
        return "Plan cleared."

    def get_context_string(self) -> str:
        """Returns a string representation of the plan for the AI context."""
        if not self.state:
            return ""

        lines = ["\n=== CURRENT PLAN ==="]
        lines.append(f"GOAL: {self.state.goal}")
        lines.append("STEPS:")
        for i, todo in enumerate(self.state.todos):
            marker = "[ ]"
            if todo.status == "active":
                marker = "[>]"
            elif todo.status == "completed":
                marker = "[x]"
            lines.append(f" {i+1}. {marker} {todo.task}")
        
        if self.state.notes:
            lines.append("NOTES:")
            for note in self.state.notes:
                lines.append(f" - {note}")
        
        lines.append("==================\n")
        return "\n".join(lines)
