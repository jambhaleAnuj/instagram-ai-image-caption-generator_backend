from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import requests
import json
from dotenv import load_dotenv
import io
import os
import torch
from gemma_call import generate

load_dotenv()

# Optimize PyTorch for small CPU instances
try:
    torch.set_num_threads(max(1, min(4, os.cpu_count() or 1)))
except Exception:
    pass

# Load the processor and model ONCE at startup (module import)
PROCESSOR = BlipProcessor.from_pretrained(
    'Salesforce/blip-image-captioning-base', use_fast=True
)
MODEL = BlipForConditionalGeneration.from_pretrained(
    'Salesforce/blip-image-captioning-base'
)
MODEL.eval()

_WARMED = False


def warm_blip():
    global _WARMED
    if _WARMED:
        return
    try:
        # Create a tiny in-memory image and run a very short generation
        img = Image.new('RGB', (2, 2), (255, 255, 255))
        inputs = PROCESSOR(images=img, return_tensors="pt")
        with torch.inference_mode():
            _ = MODEL.generate(
                **inputs,
                max_new_tokens=5,
                num_beams=1,
                do_sample=False,
                early_stopping=True,
            )
        _WARMED = True
    except Exception:
        # Do not block startup on warmup issues
        _WARMED = False


def is_blip_warmed() -> bool:
    return bool(_WARMED)


def image_classification(url):
    # Handle both file path/URL and bytes
    if isinstance(url, (bytes, bytearray)):
        image = Image.open(io.BytesIO(url))
    else:
        image = Image.open(url)

    # Ensure RGB and let the processor handle resizing/normalization
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Preprocess the image
    inputs = PROCESSOR(images=image, return_tensors="pt")

    # Generate a caption (opt for speed on CPU)
    with torch.inference_mode():
        output = MODEL.generate(
            **inputs,
            max_new_tokens=20,  # shorter generation for latency
            num_beams=1,        # greedy decoding for speed
            do_sample=False,
            early_stopping=True
        )

    # Decode the output
    caption = PROCESSOR.decode(output[0], skip_special_tokens=True)
    # Generate Instagram captions using the gemma_call module
    caption_json = generate(caption)
    return caption_json

