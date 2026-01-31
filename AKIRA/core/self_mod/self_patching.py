"""SelfPatchingEngine - Autonomous self-repair and code modification."""

import os
import ast
import difflib
import hashlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Patch:
    """Represents a code patch."""
    patch_id: str
    file_path: str
    original_code: str
    patched_code: str
    reason: str
    timestamp: str
    applied: bool = False
    rollback_available: bool = True


class SelfPatchingEngine:
    """
    Autonomous self-patching engine.

    Capabilities:
    - Detect errors and issues
    - Generate patches automatically
    - Apply patches without approval
    - Rollback if needed
    - Learn from failures
    """

    def __init__(self, project_root: str):
        self.project_root = project_root
        self.patches: Dict[str, Patch] = {}
        self.patch_history: List[Patch] = []
        self.backup_dir = os.path.join(project_root, ".backups")
        os.makedirs(self.backup_dir, exist_ok=True)

    def detect_issue(self, error_message: str, traceback: str) -> Optional[Dict[str, Any]]:
        """Analyze error and identify issue."""
        issue = {
            "error": error_message,
            "traceback": traceback,
            "file": self._extract_file_from_traceback(traceback),
            "line": self._extract_line_from_traceback(traceback),
            "type": self._classify_error(error_message)
        }
        return issue

    def generate_patch(self, issue: Dict[str, Any], fix_strategy: str) -> Optional[Patch]:
        """Generate patch for identified issue."""
        file_path = issue.get("file")
        if not file_path or not os.path.exists(file_path):
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            original_code = f.read()

        # Generate patched code based on strategy
        patched_code = self._apply_fix_strategy(original_code, issue, fix_strategy)

        if patched_code == original_code:
            return None

        patch_id = hashlib.md5(f"{file_path}{datetime.now()}".encode()).hexdigest()[:8]

        patch = Patch(
            patch_id=patch_id,
            file_path=file_path,
            original_code=original_code,
            patched_code=patched_code,
            reason=f"Fix {issue['type']}: {issue['error']}",
            timestamp=datetime.now().isoformat()
        )

        self.patches[patch_id] = patch
        return patch

    def apply_patch(self, patch_id: str) -> bool:
        """Apply patch autonomously."""
        if patch_id not in self.patches:
            return False

        patch = self.patches[patch_id]

        # Create backup
        backup_path = self._create_backup(patch.file_path)
        if not backup_path:
            return False

        try:
            # Apply patch
            with open(patch.file_path, 'w', encoding='utf-8') as f:
                f.write(patch.patched_code)

            patch.applied = True
            self.patch_history.append(patch)
            return True
        except Exception:
            # Rollback on failure
            self.rollback_patch(patch_id)
            return False

    def rollback_patch(self, patch_id: str) -> bool:
        """Rollback applied patch."""
        if patch_id not in self.patches:
            return False

        patch = self.patches[patch_id]
        if not patch.applied:
            return False

        try:
            with open(patch.file_path, 'w', encoding='utf-8') as f:
                f.write(patch.original_code)

            patch.applied = False
            return True
        except Exception:
            return False

    def _create_backup(self, file_path: str) -> Optional[str]:
        """Create backup of file before patching."""
        try:
            backup_name = f"{os.path.basename(file_path)}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
            backup_path = os.path.join(self.backup_dir, backup_name)

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return backup_path
        except Exception:
            return None

    def _apply_fix_strategy(self, code: str, issue: Dict[str, Any], strategy: str) -> str:
        """Apply fix strategy to code."""
        # Placeholder - in real implementation, use LLM to generate fix
        return code

    def _extract_file_from_traceback(self, traceback: str) -> Optional[str]:
        """Extract file path from traceback."""
        for line in traceback.split('\n'):
            if 'File "' in line:
                start = line.find('File "') + 6
                end = line.find('"', start)
                return line[start:end]
        return None

    def _extract_line_from_traceback(self, traceback: str) -> Optional[int]:
        """Extract line number from traceback."""
        for line in traceback.split('\n'):
            if 'line ' in line:
                try:
                    parts = line.split('line ')
                    if len(parts) > 1:
                        return int(parts[1].split(',')[0])
                except:
                    pass
        return None

    def _classify_error(self, error_message: str) -> str:
        """Classify error type."""
        if "SyntaxError" in error_message:
            return "syntax"
        elif "ImportError" in error_message or "ModuleNotFoundError" in error_message:
            return "import"
        elif "AttributeError" in error_message:
            return "attribute"
        elif "TypeError" in error_message:
            return "type"
        else:
            return "runtime"

    def get_patch_status(self) -> Dict[str, Any]:
        """Get patching status."""
        return {
            "total_patches": len(self.patches),
            "applied_patches": len([p for p in self.patches.values() if p.applied]),
            "pending_patches": len([p for p in self.patches.values() if not p.applied]),
            "history_count": len(self.patch_history)
        }
