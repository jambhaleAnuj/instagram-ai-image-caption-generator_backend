from blip_image_classification import image_classification, warm_blip, is_blip_warmed
#     caption_json = image_classification(url)


# if __name__ == "__main__":

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI()

# Broad CORS for demo; restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Warm BLIP on startup in a thread to avoid blocking
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, warm_blip)

@app.get("/")
async def root():
    return {"message": "Welcome to the Instagram AI Image Caption Maker API!"}

@app.get("/healthz")
async def health():
    return {"status": "ok"}

@app.get("/readyz")
async def ready():
    return {"ready": is_blip_warmed()}

@app.post("/upload_image/")
async def upload_image(file: UploadFile = File(...)):
    # Validate image type by content type
    if not file.content_type or not file.content_type.startswith('image/'):
        return JSONResponse(status_code=400, content={"message": "Invalid file type. Please upload an image."})

    image_bytes = await file.read()

    # Run CPU-heavy work in a threadpool so the event loop stays responsive
    loop = asyncio.get_event_loop()
    caption_json = await loop.run_in_executor(None, image_classification, image_bytes)

    if caption_json:
        return JSONResponse(status_code=200, content=caption_json)
    else:
        return JSONResponse(status_code=502, content={"message": "Failed to generate captions."})


if __name__ == "__main__":
    uvicorn.run(app, port=3000)