import asyncio
import logging

from faster_whisper import WhisperModel

logger = logging.getLogger("mirofish.interface.voice.stt")

class SpeechToText:
    """
    Local Whisper STT using faster-whisper.
    Quantized to int8 and run on CPU to save RAM.
    """
    def __init__(self, model_size: str = "base") -> None:
        self.model_size = model_size
        logger.info(f"Loading Whisper {model_size} (int8 on CPU)...")
        # Run on CPU with int8 to stay under the 16GB RAM constraint
        self.model = WhisperModel(self.model_size, device="cpu", compute_type="int8")

    async def transcribe(self, audio_file_path: str) -> str:
        """
        Asynchronously transcribes audio.
        Offloads the blocking CPU bound inference to a thread pool.
        """
        loop = asyncio.get_running_loop()
        def _transcribe() -> str:
            segments, _ = self.model.transcribe(audio_file_path, beam_size=5)
            text = " ".join([segment.text for segment in segments])
            return text.strip()
            
        logger.debug(f"Transcribing {audio_file_path}")
        text = await loop.run_in_executor(None, _transcribe)
        return text
