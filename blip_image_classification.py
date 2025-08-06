from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import requests
import json
from dotenv import load_dotenv
import os
load_dotenv()
from gemma_call import generate


def image_classification(url):
    
    # Load the processor and model
    processor = BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-base', use_fast = True)
    model = BlipForConditionalGeneration.from_pretrained('Salesforce/blip-image-captioning-base')

    # Handle both file path/URL and bytes
    if isinstance(url, (bytes, bytearray)):
        import io
        image = Image.open(io.BytesIO(url))
    else:
        image = Image.open(url)

    # Preprocess the image
    inputs = processor(images=image, return_tensors="pt")

    # Generate a caption
    output = model.generate(**inputs)

    # Decode the output
    caption = processor.decode(output[0], skip_special_tokens=True)
    print("Generated Caption:", caption)
    # Generate Instagram captions using the gemma_call module
    caption_json = generate(caption)
    return caption_json

