import logging
import os
import asyncio

logger = logging.getLogger("mirofish.evolution.local_llm")

class AirLLMEngine:
    """
    Customized AirLLM Integration for MiroFish OS.
    Allows running massive models (70B+) on local 4GB/8GB GPUs using Layer-wise Inference.
    Used automatically if Cloud APIs fail or if 'Offline/Private' mode is requested.
    """
    def __init__(self, model_id: str = "garage-bAInd/Platypus2-70B-instruct"):
        self.model_id = model_id
        self.model = None
        self.is_loaded = False
        self._lock = asyncio.Lock()

    def _lazy_load_model(self):
        """Loads the model into RAM/GPU only when first needed to save resources."""
        if not self.is_loaded:
            logger.info(f"🚀 Initializing AirLLM Engine with {self.model_id}...")
            logger.warning("This will take significant RAM and run using layer-wise swapping.")
            try:
                # We import here so the rest of the OS doesn't crash if airllm isn't installed
                from airllm import AutoModel
                # Customized settings: compression=None or '4bit' depending on hardware
                self.model = AutoModel.from_pretrained(self.model_id)
                self.is_loaded = True
                logger.info("AirLLM loaded successfully.")
            except ImportError:
                logger.error("airllm package not found. Please run 'pip install airllm'")
            except Exception as e:
                logger.error(f"Failed to load AirLLM model: {e}")

    async def generate_offline(self, prompt: str, max_new_tokens: int = 512) -> str:
        """
        Executes an inference request locally.
        """
        async with self._lock:
            if not self.is_loaded:
                self._lazy_load_model()
                
            if not self.model:
                return "System Error: AirLLM engine could not be started."
            
            try:
                logger.info(f"Generating offline response using AirLLM for prompt length: {len(prompt)}")
                
                # AirLLM uses standard tokenizers
                # (Assuming transformers is installed)
                from transformers import AutoTokenizer
                tokenizer = AutoTokenizer.from_pretrained(self.model_id)
                
                inputs = tokenizer([prompt], return_tensors="pt")
                # Move to cuda if available is handled internally by AirLLM usually
                
                # In a real async loop we'd run this blocking call in a threadpool
                loop = asyncio.get_running_loop()
                
                def _run_inference():
                    # AirLLM standard generation
                    output = self.model.generate(
                        inputs["input_ids"],
                        max_new_tokens=max_new_tokens,
                        use_cache=True,
                        return_dict_in_generate=True
                    )
                    return tokenizer.decode(output.sequences[0], skip_special_tokens=True)
                
                result = await loop.run_in_executor(None, _run_inference)
                return result
                
            except Exception as e:
                logger.error(f"Offline generation failed: {e}")
                return f"Error running local inference: {str(e)}"

# Singleton for the OS Router
offline_llm_engine = AirLLMEngine()
