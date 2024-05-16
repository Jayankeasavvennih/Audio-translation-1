from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
import assemblyai as aai
from googletrans import Translator, LANGUAGES
import gtts as gt
import pygame
import requests
import os
from io import BytesIO
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

aai.settings.api_key = "488d4da6a90d4c67b93b99866def037f"

# class AudioTranslation(BaseModel):
#     audio_file: UploadFile

@app.post("/translate")
async def translate_audio(audio_file: UploadFile = File(...)):
    try:
        # Create a directory to store the audio files within the server
        upload_dir = "uploaded_audio"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save the uploaded audio file to disk
        audio_file_path = os.path.join(upload_dir, audio_file.filename)
        with open(audio_file_path, "wb") as file:
            content = await audio_file.read()
            file.write(content)

        # Transcribe audio using AssemblyAI
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_file_path)
        english_text = transcript.text
        print("english_text",english_text)

        # Translate English text to Tamil
        # translator = Translator()
        # print("translator",translator)
        # try:
        #     translation = translator.translate(english_text, src='en', dest='ta')
        #     tamil_text = translation.text
        # except Exception as e:
        #     raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")
        # print("tamil_text",tamil_text)

        # Translate English text to Tamil using MyMemory API
        try:
            response = requests.get(
                "https://api.mymemory.translated.net/get",
                params={
                    "q": english_text,
                    "langpair": "en|ta"
                }
            )
            response.raise_for_status()
            translation = response.json()
            tamil_text = translation['responseData']['translatedText']
        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

        print("tamil_text", tamil_text)
        

        # Convert Tamil text to speech
        tts = gt.gTTS(text=tamil_text, lang='ta')
        audio_output = BytesIO()
        tts.write_to_fp(audio_output)
        audio_output.seek(0)

        # Save the audio file
        output_path = "audio/output.mp3"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(audio_output.read())

        return {"message": "Audio generated successfully", "output_path": output_path}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_root():
    return {"message": "welcome"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
