import pytest
from mirofish_os.monetization.keystone import KeystonePartitioner

def test_80_20_partitioning():
    partitioner = KeystonePartitioner()
    
    full_artifact = "\n".join([f"Line {i}" for i in range(10)])
    
    proof, keystone = partitioner.partition_solution("sol_1", full_artifact)
    
    # Proof should contain 8 lines (80% of 10)
    assert "Line 7" in proof
    assert "Line 8" not in proof
    assert "[PAYMENT REQUIRED" in proof
    
    # Keystone should contain the remaining 2 lines
    assert "Line 8" in keystone
    assert "Line 9" in keystone
    
    # Unlock retrieves the keystone
    unlocked = partitioner.unlock("sol_1")
    assert unlocked == keystone
