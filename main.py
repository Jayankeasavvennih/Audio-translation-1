from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import assemblyai as aai
from googletrans import Translator
import gtts as gt
import pygame
import requests
import os
from io import BytesIO
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

aai.settings.api_key = "488d4da6a90d4c67b93b99866def037f"

class AudioTranslation(BaseModel):
    url: str

@app.post("/translate")
async def translate_audio(audio_translation: AudioTranslation):
    try:
        url = audio_translation.url

        # Check if URL is accessible
        response = requests.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Failed to access audio file.")

        # Transcribe audio using AssemblyAI
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(url)
        english_text = transcript.text

        # Translate English text to Tamil
        translator = Translator()
        translation = translator.translate(english_text, src='en', dest='ta')
        tamil_text = translation.text

        # Convert Tamil text to speech
        tts = gt.gTTS(text=tamil_text, lang='ta')
        audio_file = BytesIO()
        tts.write_to_fp(audio_file)
        audio_file.seek(0)

        # Save the audio file
        output_path = "audio/output.mp3"  # Define your desired output path
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(audio_file.read())

        # Play the audio file
        pygame.mixer.init()
        pygame.mixer.music.load(output_path)
        pygame.mixer.music.play()

        # Wait until the audio finishes playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        return {"message": "Audio generated successfully", "output_path": output_path}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
