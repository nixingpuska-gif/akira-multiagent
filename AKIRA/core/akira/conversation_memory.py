"""
AKIRA Conversation Memory
Stores and retrieves conversation history
"""

import json
import os
from typing import List, Dict, Any
from datetime import datetime
from collections import defaultdict


class ConversationMemory:
    """
    Manages conversation history for each user.
    Stores messages and provides context for AI.
    """

    def __init__(self, storage_path: str = "data/conversations"):
        self.storage_path = storage_path
        self.conversations: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
        self.max_history = 50  # Keep last 50 messages per user
        self._load_conversations()

    def _load_conversations(self):
        """Load conversations from disk."""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path, exist_ok=True)
            return

        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                user_id = int(filename.replace('.json', ''))
                filepath = os.path.join(self.storage_path, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        self.conversations[user_id] = json.load(f)
                except Exception as e:
                    print(f"Error loading conversation for {user_id}: {e}")

    def _save_conversation(self, user_id: int):
        """Save conversation to disk."""
        os.makedirs(self.storage_path, exist_ok=True)
        filepath = os.path.join(self.storage_path, f"{user_id}.json")
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.conversations[user_id], f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving conversation for {user_id}: {e}")

    def add_message(self, user_id: int, role: str, content: str):
        """Add message to conversation history."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }

        self.conversations[user_id].append(message)

        # Keep only last N messages
        if len(self.conversations[user_id]) > self.max_history:
            self.conversations[user_id] = self.conversations[user_id][-self.max_history:]

        self._save_conversation(user_id)

    def get_history(self, user_id: int, last_n: int = 10) -> List[Dict[str, Any]]:
        """Get last N messages for user."""
        return self.conversations[user_id][-last_n:]

    def get_context_string(self, user_id: int, last_n: int = 5) -> str:
        """Get conversation context as formatted string."""
        history = self.get_history(user_id, last_n)

        if not history:
            return ""

        context_lines = ["Предыдущий контекст разговора:"]
        for msg in history:
            role = "Пользователь" if msg["role"] == "user" else "AKIRA"
            context_lines.append(f"{role}: {msg['content'][:200]}")

        return "\n".join(context_lines)

    def clear_history(self, user_id: int):
        """Clear conversation history for user."""
        self.conversations[user_id] = []
        self._save_conversation(user_id)
