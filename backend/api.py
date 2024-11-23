from fastapi import APIRouter, Header, HTTPException, UploadFile, File, Cookie
from fastapi.responses import JSONResponse
from typing import Annotated
import os
from dotenv import load_dotenv
from pathlib import Path
from uuid import uuid4
import whisper
import openai

load_dotenv()

AUTHORIZATION_KEY = os.getenv("AUTHORIZATION_KEY")

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

router = APIRouter()

model = whisper.load_model("base")

openai.api_key = os.getenv("OPENAI_API_KEY")


@router.post("/upload")
async def upload_audio(
    authorization: str = Annotated[
        str,
        Header(..., description="Authorization Key", alias="Authorization"),
    ],
    audio: UploadFile = Annotated[UploadFile, File(...)],
):
    if authorization != AUTHORIZATION_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        # Save the uploaded audio file
        file_path = UPLOAD_DIR / f"{uuid4}-{audio.filename}"
        with open(file_path, "wb") as f:
            f.write(await audio.read())

        # Transcribe the audio using Whisper
        result = model.transcribe(str(file_path))
        transcription = result["text"]
        print("Transcription:", transcription)

        # Send transcription to ChatGPT
        response = openai.ChatCompletion.create(
            model="gpt-4", messages=[{"role": "user", "content": transcription}]
        )
        chatgpt_response = response["choices"][0]["message"]["content"]
        print("ChatGPT Response:", chatgpt_response)

        # Delete the file after processing
        try:
            os.remove(file_path)
        except FileNotFoundError:
            pass

        # Return the response
        return JSONResponse(
            {"transcription": transcription, "chatgpt_response": chatgpt_response}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
