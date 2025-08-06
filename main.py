from blip_image_classification import image_classification
#     caption_json = image_classification(url)


# if __name__ == "__main__":

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Instagram AI Image Caption Maker API!"}
@app.post("/upload_image/")
async def upload_image(file:UploadFile = File(...)):
    #Validate image type by content type
    if not file.content_type.startswith('image/'):
        return JSONResponse(status_code=400, content={"message": "Invalid file type. Please upload an image."})
    
    # Read image bytes
    image_bytes = await file.read()
    caption_json = image_classification(image_bytes)
    print(caption_json)
    if caption_json:
        return JSONResponse(status_code=200, content=caption_json)
    else:
        return JSONResponse(status_code=500, content={"message": "Failed to generate captions."})
    

if __name__ == "__main__":
    uvicorn.run(app, port=3000)