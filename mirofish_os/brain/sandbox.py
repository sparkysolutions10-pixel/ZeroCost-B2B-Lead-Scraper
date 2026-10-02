import logging
import os
import shutil

from ..config.settings import settings

logger = logging.getLogger("mirofish.brain.sandbox")

class WorkspaceSandbox:
    """
    Workspace Isolation Manager.
    Creates, validates, and cleans up jailed sub-folders per task.
    """
    def __init__(self, base_dir: str = settings.WORKSPACE_DIR):
        self.base_dir = os.path.abspath(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)

    def create_sandbox(self, task_id: str) -> str:
        path = os.path.join(self.base_dir, f"task_{task_id}")
        os.makedirs(path, exist_ok=True)
        logger.info(f"Isolated sandbox created: {path}")
        return path

    def is_path_safe(self, sandbox_dir: str, target_path: str) -> bool:
        """Prevents path traversal attacks by ensuring operations stay in the sandbox."""
        abs_target = os.path.abspath(target_path)
        abs_sandbox = os.path.abspath(sandbox_dir)
        return abs_target.startswith(abs_sandbox)

    def destroy_sandbox(self, task_id: str) -> None:
        path = os.path.join(self.base_dir, f"task_{task_id}")
        if os.path.exists(path) and self.is_path_safe(self.base_dir, path):
            shutil.rmtree(path)
            logger.info(f"Sandbox {path} destroyed.")
