
# Instagram AI Image Caption Maker (Backend)


##  Unique Privacy Advantage (USP)
**Your images are never sent to Google, OpenAI, or any third-party servers.** The BLIP model runs locally to generate a description of your image, and only this text description is sent to Gemini/Gemma for creative caption generation. This ensures your image data remains private and secure—ideal for privacy-conscious users and businesses.


> **Note:** This repository contains only the backend API. You can build your own frontend (web, mobile, etc.) to interact with this API, or integrate it into your existing workflow.

Generate creative, human-like, and SEO-optimized Instagram captions for your images using state-of-the-art AI models (BLIP + Google Gemini/Gemma). This project provides a FastAPI backend that accepts image uploads and returns a variety of engaging captions in multiple styles, perfect for boosting your Instagram presence.

##  Features
- **AI-Powered Captions:** Uses BLIP for image understanding and Google Gemini/Gemma for creative caption generation.
- **Multiple Caption Styles:** Get captions in styles like Witty, Inspirational, Minimalist, Poetic, and more.
- **FastAPI Backend:** Simple REST API for easy integration.
- **CORS Enabled:** Ready for frontend and cross-origin requests.
- **SEO-Optimized Output:** Captions are designed to maximize discoverability and engagement.

##  Example Output
```json
[
  {
    "style": "Witty",
    "captions": [
      "Just a frame...waiting for its masterpiece. 😏 #artinprogress #blankcanvas #justkidding #photography #blackandwhite",
      "This frame is accepting applications for stories. ✍️  Send your best! #storytime #potential #creative #photography #blackandwhite"
    ]
  },
  {
    "style": "Inspirational",
    "captions": [
      "The space to create. The space to grow. ✨ Your story is waiting to be written. #inspiration #motivation #create #grow #photography",
      "Embrace the blank page.  Every moment is a chance to start anew. 💍 #newbeginnings #possibilities #positivevibes #photography #blackandwhite"
    ]
  }
]
```

##  Getting Started

### Prerequisites
- Python 3.8+
- [Google API Key](https://ai.google.dev/) for Gemini/Gemma

### Installation
1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/instagram-ai-image-caption-maker.git
   cd instagram-ai-image-caption-maker/Backend
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Set up environment variables:**
   - Create a `.env` file in the `Backend` directory:
     ```env
     GOOGLE_API_KEY=your_google_api_key_here
     ```

### Running the API
```sh
uvicorn main:app --port 3000
```

### API Usage
- **POST** `/upload_image/`
  - Form-data: `file` (image)
  - Returns: JSON with multiple caption styles

##  Tech Stack
- Python, FastAPI, Uvicorn
- HuggingFace Transformers (BLIP)
- Google Gemini/Gemma (via google-genai)
- Pillow, dotenv, requests

##  License
MIT License

##  Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

##  SEO Keywords
Instagram AI caption generator, image captioning, FastAPI, BLIP, Gemini, Gemma, social media automation, creative captions, SEO Instagram captions, Python, open source, content creator tools

##  Star This Project!
If you find this project useful, please give it a star on GitHub to help others discover it!
