from transformers import Blip2Processor, Blip2ForConditionalGeneration
from PIL import Image
from dotenv import load_dotenv
import io
import os
import torch
import threading
from gemma_call import generate

load_dotenv()

# Optimize PyTorch for small CPU instances
try:
    torch.set_num_threads(max(1, min(4, os.cpu_count() or 1)))
except Exception:
    pass

# Config toggles
LOCAL_ONLY = os.getenv("HF_LOCAL_ONLY", "1") == "1"
CPU_QUANT = os.getenv("CPU_QUANTIZE", "0") == "1"
BLIP2_MODEL_ID = os.getenv("BLIP2_MODEL_ID", "Salesforce/blip2-opt-2.7b")

# Lazy-loaded globals
PROCESSOR = None
MODEL = None
_LOAD_LOCK = threading.Lock()

_WARMED = False


def _ensure_blip2():
    global PROCESSOR, MODEL
    if PROCESSOR is not None and MODEL is not None:
        return
    with _LOAD_LOCK:
        if PROCESSOR is not None and MODEL is not None:
            return
        processor = Blip2Processor.from_pretrained(
            BLIP2_MODEL_ID, use_fast=True, local_files_only=LOCAL_ONLY
        )
        model = Blip2ForConditionalGeneration.from_pretrained(
            BLIP2_MODEL_ID, low_cpu_mem_usage=True, local_files_only=LOCAL_ONLY
        )
        if CPU_QUANT:
            try:
                model = torch.quantization.quantize_dynamic(
                    model, {torch.nn.Linear}, dtype=torch.qint8
                )
            except Exception:
                # Best-effort; continue without quantization if unavailable
                pass
        model.eval()
        PROCESSOR = processor
        MODEL = model


def warm_blip():
    global _WARMED
    if _WARMED:
        return
    try:
        _ensure_blip2()
        # Create a tiny in-memory image and run a very short generation
        img = Image.new('RGB', (2, 2), (255, 255, 255))
        # BLIP-2 benefits from a short prompt; keep it minimal
        inputs = PROCESSOR(images=img, text="a photo of", return_tensors="pt")
        with torch.inference_mode():
            _ = MODEL.generate(
                **inputs,
                max_new_tokens=5,
                num_beams=1,
                do_sample=False,
            )
        _WARMED = True
    except Exception:
        # Do not block startup on warmup issues
        _WARMED = False


def is_blip_warmed() -> bool:
    return bool(_WARMED)


def image_classification(url):
    _ensure_blip2()
    # Handle both file path/URL and bytes
    if isinstance(url, (bytes, bytearray)):
        image = Image.open(io.BytesIO(url))
    else:
        image = Image.open(url)

    # Ensure RGB and let the processor handle resizing/normalization
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Preprocess the image (BLIP-2 often uses a short guiding prompt)
    inputs = PROCESSOR(images=image, text="Describe the image.", return_tensors="pt")

    # Generate a caption (opt for speed on CPU)
    with torch.inference_mode():
        output = MODEL.generate(
            **inputs,
            max_new_tokens=20,  # shorter generation for latency
            num_beams=1,        # greedy decoding for speed
            do_sample=False,
        )

    # Decode the output using BLIP-2 tokenizer
    caption = PROCESSOR.tokenizer.batch_decode(output, skip_special_tokens=True)[0].strip()
    # Generate Instagram captions using the gemma_call module
    caption_json = generate(caption)
    return caption_json

