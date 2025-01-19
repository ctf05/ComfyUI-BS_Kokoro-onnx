import comfy.sample as comfy_sample
import numpy as np
import torch
from kokoro_onnx import Kokoro
import logging
import os
import requests
from tqdm import tqdm

logger = logging.getLogger(__name__)

MODEL_URL = "https://huggingface.co/thewh1teagle/kokoro-onnx/resolve/main/kokoro-v0_19.onnx"
VOICES_URL = "https://huggingface.co/thewh1teagle/kokoro-onnx/resolve/main/voices.json"

class KokoroTTS:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "Check out BS Labs youtube channel: https://www.youtube.com/channel/UCcYXt5R6tpQgKYxULWYD95Q"}),
                "speaker": (
                    [
                        "af",
                        "af_sarah",
                        "af_bella",
                        "af_nicole",
                        "af_sky",
                        "am_adam",
                        "am_michael",
                        "bf_emma",
                        "bf_isabella",
                        "bm_george",
                        "bm_lewis",
                    ],
                    {"default": "af_sarah"},
                ),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)

    FUNCTION = "generate"

    CATEGORY = "kokoro"

    def __init__(self):
        self.kokoro = None
        logger.info("Initializing KokoroTTS class.")
        # Get the directory where nodes.py is located
        node_dir = os.path.dirname(os.path.abspath(__file__))
         # Get the full path to the directory
        self.model_path = os.path.join(node_dir, "kokoro-v0_19.onnx")
        self.voices_path = os.path.join(node_dir, "voices.json")


    def generate(self, text, speaker):

        if not os.path.exists(self.model_path) or not os.path.exists(self.voices_path):
            logger.error(f"ERROR: model or voice file not found. Please download them manually from {MODEL_URL} and {VOICES_URL} and place them in the same folder as the node. model_path: {self.model_path}, voices_path: {self.voices_path}")
            return (None,)

        try:
            kokoro = Kokoro(model_path=self.model_path, voices_path=self.voices_path)
        except Exception as e:
             logger.error(f"ERROR: could not load kokoro-onnx in generate: {e}")
             return (None,)

        try:
            audio, sample_rate = kokoro.create(text, voice=speaker, speed=1.0, lang="en-us")
        except Exception as e:
            logger.error(f"ERROR: could not generate speech using kokoro.create. Error: {e}")
            return (None,)

        if audio is None:
             logger.error("ERROR: the text-to-speech generation did not return audio. Make sure you have a valid text string.")
             return (None,)

        # Convert the numpy array to the format expected by comfy audio output
        audio_tensor = torch.from_numpy(audio).unsqueeze(0).unsqueeze(0).float()  # Add a batch dimension AND a channel dimension

        logger.info(f"Successfuly generated audio. Audio shape: {audio_tensor.shape}. Audio length: {len(audio)}")
        return ({"waveform": audio_tensor, "sample_rate": sample_rate},) #return as tuple

    @classmethod
    def IS_CHANGED(cls, text, speaker):
        return hash((text, speaker))

NODE_CLASS_MAPPINGS = {
    "Kokoro TTS": KokoroTTS,
}