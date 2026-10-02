import logging
import os
import uuid

import edge_tts

logger = logging.getLogger("mirofish.interface.voice.tts")

class TextToSpeech:
    """
    Streaming Text-to-Speech using edge-tts.
    Provides fast, free high-quality voices without loading heavy models into RAM.
    """
    def __init__(self, voice: str = "en-US-AriaNeural") -> None:
        self.voice = voice

    async def synthesize(self, text: str, output_dir: str = "/tmp") -> str:
        """
        Generates an audio file from text.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            
        filename = f"tts_{uuid.uuid4().hex}.mp3"
        filepath = os.path.join(output_dir, filename)
        
        logger.debug(f"Synthesizing speech to {filepath}")
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(filepath)
        return filepath
