import logging
import os
import shutil
import subprocess

from ..config.settings import settings

logger = logging.getLogger("mirofish.evolution.shadow_sandbox")

class ShadowSandbox:
    """
    Isolated hot-reload & testing environment.
    Mythos AI tests its newly written code here before overwriting main files.
    """
    def __init__(self, sandbox_dir: str = settings.SHADOW_SANDBOX_DIR):
        self.sandbox_dir = os.path.abspath(sandbox_dir)

    def prepare_environment(self, target_module: str) -> str:
        """Copies a target module to the shadow sandbox for testing."""
        os.makedirs(self.sandbox_dir, exist_ok=True)
        target_path = os.path.abspath(target_module)
        if not os.path.exists(target_path):
            raise FileNotFoundError(f"Module {target_path} not found.")
            
        shadow_path = os.path.join(self.sandbox_dir, os.path.basename(target_module))
        
        if os.path.isdir(target_path):
            if os.path.exists(shadow_path):
                shutil.rmtree(shadow_path)
            shutil.copytree(target_path, shadow_path)
        else:
            shutil.copy2(target_path, shadow_path)
            
        logger.info(f"Prepared shadow environment for {target_module} at {shadow_path}")
        return shadow_path

    def run_tests(self) -> bool:
        """Runs the pytest suite inside the sandbox context."""
        logger.info("Executing test suite in Shadow Sandbox...")
        try:
            # We assume tests are written in a way they can target the shadow_sandbox module.
            # E.g. pytest tests/
            result = subprocess.run(["pytest", "tests/"], capture_output=True, text=True, cwd=os.getcwd(), check=False)
            if result.returncode == 0:
                logger.info("Shadow tests passed successfully.")
                return True
            else:
                logger.warning(f"Shadow tests failed!\n{result.stdout}\n{result.stderr}")
                return False
        except FileNotFoundError:
            logger.error("pytest not found. Assuming tests failed.")
            return False

    def promote_code(self, shadow_path: str, live_path: str) -> None:
        """Hot-swaps the verified code to the live directory."""
        logger.info(f"Promoting verified code from {shadow_path} to {live_path}")
        if os.path.isdir(shadow_path):
            shutil.rmtree(live_path)
            shutil.copytree(shadow_path, live_path)
        else:
            shutil.copy2(shadow_path, live_path)
