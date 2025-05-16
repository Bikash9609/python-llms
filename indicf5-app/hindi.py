from transformers.models.auto.modeling_auto import AutoModel
import numpy as np
import soundfile as sf
import os
import logging
from huggingface_hub import login
from dotenv import load_dotenv

load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Hugging Face login
hf_token = os.getenv('HF_TOKEN')
login(hf_token)

# Load model
repo_id = "ai4bharat/IndicF5"

try:
    model = AutoModel.from_pretrained(repo_id, trust_remote_code=True, device_map='mps')
    logging.info("✅ Model loaded successfully!")
except Exception as e:
    logging.error(f"❌ Error loading model: {e}")
    exit(1)

# Hindi TTS input
text = "नमस्ते! आज का दिन बहुत अच्छा है।"
ref_audio_path = "1.wav"
ref_text = "नमस्ते! यह एक परीक्षण है।"

if not os.path.exists(ref_audio_path):
    logging.error(f"❌ Reference audio not found: {ref_audio_path}")
    exit(1)

try:
    logging.info("🎤 Generating Hindi speech...")
    audio_data = model(
        text=text,
        ref_audio_path=ref_audio_path,
        ref_text=ref_text,
    )

    if audio_data is None or len(audio_data) == 0:
        logging.error("❌ No audio data generated!")
        exit(1)

    def normalize_audio(audio_array):
        audio_array = np.asarray(audio_array)
        return audio_array.astype(np.float32) / np.max(np.abs(audio_array))

    output_dir = "IndicF5/output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "hindi_speech.wav")

    sf.write(output_path, normalize_audio(audio_data), samplerate=24000)
    logging.info(f"✅ Hindi speech generated at: {output_path}")

except Exception as e:
    logging.error(f"❌ Error during TTS generation: {e}")
