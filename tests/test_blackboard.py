import pytest
import asyncio
from mirofish_os.brain.blackboard import NoticeBoard

@pytest.mark.asyncio
async def test_blackboard_pubsub():
    board = NoticeBoard()
    received = []
    
    async def subscriber(topic, content):
        received.append((topic, content))
        
    board.subscribe("test.topic", subscriber)
    
    await board.pin("test.topic", {"status": "ok"})
    await board.pin("other.topic", {"status": "ignore"})
    
    # Allow async subscriber to process
    await asyncio.sleep(0.1)
    
    data = await board.read("test.topic")
    assert len(data) == 1
    assert data[0]["status"] == "ok"
    
    assert len(received) == 1
    assert received[0][0] == "test.topic"
    assert received[0][1]["status"] == "ok"
