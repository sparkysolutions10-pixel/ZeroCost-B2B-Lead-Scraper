import logging

logger = logging.getLogger("mirofish.monetization.keystone")

class KeystonePartitioner:
    """
    Implements the 80/20 Keystone Strategy.
    Splits a solution into a 'Proof of Value' (80%) and the 'Keystone Unlock' (20%).
    """
    
    def __init__(self) -> None:
        self.pending_unlocks: dict[str, str] = {}

    def partition_solution(self, solution_id: str, full_artifact: str) -> tuple[str, str]:
        """
        Takes a full artifact (e.g. source code, analysis report) and splits it.
        Returns (proof_payload, keystone_payload).
        """
        # Very simple split logic for demonstration.
        # A true implementation would intelligently redact configuration, master weights, or concluding paragraphs.
        
        lines = full_artifact.split('\n')
        split_idx = int(len(lines) * 0.8)
        
        proof_payload = "\n".join(lines[:split_idx])
        proof_payload += "\n\n[=== END OF PROOF ===]\n[PAYMENT REQUIRED TO UNLOCK REMAINING 20% KEYSTONE]"
        
        keystone_payload = "\n".join(lines[split_idx:])
        
        # Store the locked portion in memory (or SQLite) mapped to the solution_id/checkout_session_id
        self.pending_unlocks[solution_id] = keystone_payload
        
        logger.info(f"Solution {solution_id} partitioned into 80/20 strategy.")
        return proof_payload, keystone_payload

    def unlock(self, solution_id: str) -> str:
        """Retrieves the 20% payload if payment clears."""
        if solution_id in self.pending_unlocks:
            logger.info(f"Unlocking Keystone for solution {solution_id}")
            return self.pending_unlocks.pop(solution_id)
        return ""

keystone_engine = KeystonePartitioner()
