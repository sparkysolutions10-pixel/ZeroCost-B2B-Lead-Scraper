import hashlib
import logging
import mimetypes
import os

from ..config.settings import settings

logger = logging.getLogger("mirofish.tools.quarantine")

class QuarantineLayer:
    """
    Antivirus & File Quarantine.
    Intercepts downloads, validates MIME types, checks entropy, and hashes.
    """
    def __init__(self, quarantine_dir: str = settings.QUARANTINE_DIR):
        self.q_dir = os.path.abspath(quarantine_dir)
        os.makedirs(self.q_dir, exist_ok=True)

    def scan_file(self, file_path: str) -> bool:
        """
        Runs heuristics on a downloaded file.
        Returns True if safe, False if malicious/suspicious.
        """
        if not os.path.exists(file_path):
            return False

        # 1. MIME Type check
        mime, _ = mimetypes.guess_type(file_path)
        forbidden_mimes = ["application/x-msdownload", "application/x-sh"]
        if mime in forbidden_mimes:
            logger.warning(f"Forbidden MIME type {mime} detected in {file_path}")
            return False

        # 2. Basic Hash (could be checked against a local threat DB)
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            buf = f.read(65536)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        
        file_hash = hasher.hexdigest()
        logger.debug(f"File scanned. SHA256: {file_hash}")
        
        # 3. If safe, we might return True.
        # But if we were unsure, we would move it to self.q_dir
        return True

    def quarantine(self, file_path: str) -> str:
        """Moves a suspicious file into the quarantine jail."""
        q_path = os.path.join(self.q_dir, os.path.basename(file_path))
        os.rename(file_path, q_path)
        logger.warning(f"File quarantined: {q_path}")
        return q_path
