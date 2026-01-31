"""
AKIRA Task Classifier
Determines if request needs PC execution or just AI response
"""

from typing import Dict, Any, Tuple
from enum import Enum


class TaskType(Enum):
    """Types of tasks AKIRA can handle."""
    CHAT = "chat"           # Just AI response
    PC_COMMAND = "pc"       # Execute on PC
    FILE_OP = "file"        # File operations
    CODE_EXEC = "code"      # Run code
    SYSTEM = "system"       # System operations


class TaskClassifier:
    """
    Classifies user requests to determine execution method.
    """

    # Keywords indicating PC access needed
    PC_KEYWORDS_RU = [
        "создай", "открой", "запусти", "установи", "скачай",
        "удали", "переименуй", "скопируй", "перемести",
        "покажи файлы", "список файлов", "что на диске",
        "выполни", "запусти команду", "терминал",
        "проверь систему", "диагностика", "процессы",
        "папка", "директория", "каталог"
    ]

    PC_KEYWORDS_EN = [
        "create", "open", "run", "install", "download",
        "delete", "rename", "copy", "move",
        "show files", "list files", "execute",
        "run command", "terminal", "shell",
        "check system", "diagnostics", "processes",
        "folder", "directory"
    ]

    CODE_KEYWORDS = [
        "python", "pip", "npm", "node", "git",
        "compile", "build", "test", "debug"
    ]

    def __init__(self):
        self.all_pc_keywords = self.PC_KEYWORDS_RU + self.PC_KEYWORDS_EN

    def classify(self, message: str) -> Tuple[TaskType, float]:
        """
        Classify user message.

        Args:
            message: User's message

        Returns:
            Tuple of (TaskType, confidence)
        """
        message_lower = message.lower()

        # Check for PC keywords
        pc_score = self._calculate_pc_score(message_lower)

        # Check for code keywords
        code_score = self._calculate_code_score(message_lower)

        # Determine task type
        if pc_score > 0.6:
            return TaskType.PC_COMMAND, pc_score
        elif code_score > 0.5:
            return TaskType.CODE_EXEC, code_score
        else:
            return TaskType.CHAT, 1.0 - max(pc_score, code_score)

    def _calculate_pc_score(self, message: str) -> float:
        """Calculate probability that PC access is needed."""
        matches = sum(1 for kw in self.all_pc_keywords if kw in message)
        if matches == 0:
            return 0.0
        return min(1.0, matches * 0.3 + 0.3)

    def _calculate_code_score(self, message: str) -> float:
        """Calculate probability that code execution is needed."""
        matches = sum(1 for kw in self.CODE_KEYWORDS if kw in message)
        if matches == 0:
            return 0.0
        return min(1.0, matches * 0.25 + 0.25)

    def get_action_description(self, task_type: TaskType) -> str:
        """Get human-readable description of action."""
        descriptions = {
            TaskType.CHAT: "AI Response",
            TaskType.PC_COMMAND: "PC Command Execution",
            TaskType.FILE_OP: "File Operation",
            TaskType.CODE_EXEC: "Code Execution",
            TaskType.SYSTEM: "System Operation"
        }
        return descriptions.get(task_type, "Unknown")
