from fastapi import APIRouter, Header, HTTPException, UploadFile, File, Body
from fastapi.responses import JSONResponse
from typing import Annotated
import os
from dotenv import load_dotenv
from pathlib import Path
from uuid import uuid4
import whisper
import openai
from RestrictedPython import compile_restricted
from RestrictedPython import safe_globals
import json

load_dotenv()

AUTHORIZATION_KEY = os.getenv("AUTHORIZATION_KEY")

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

router = APIRouter()

model = whisper.load_model("base")

openai.api_key = os.getenv("OPENAI_API_KEY")


SESSIONS = {}

with open("solutions.json", "r") as f:
    SOLUTIONS = json.load(f)


def check_leetcode_solution(
    code: str, func: str, solutions: list, *input: list
) -> bool:
    try:
        compiled_code = compile_restricted(code, "<string>", "exec")
        exec(compiled_code, safe_globals, {})

        if "Solution" in safe_globals and hasattr(safe_globals["Solution"], func):
            result = safe_globals["Solution"]().__getattribute__(func)(*input)
            if result in solutions:
                return True
        return False
    except Exception:
        return True


@router.post("/check-code")
async def check_code(
    authorization: str = Annotated[
        str,
        Header(..., description="Authorization Key", alias="Authorization"),
    ],
    question_id: str = Annotated[
        str,
        Body(..., description="LeetCode Question ID", alias="question_id"),
    ],
    code: str = Annotated[str, Body(..., description="Code to check", alias="code")],
):
    if authorization != AUTHORIZATION_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    func = SOLUTIONS[question_id]["func"]
    for testcase in SOLUTIONS[question_id]["testcases"]:
        if not check_leetcode_solution(
            code, func, testcase["solutions"], *testcase["input"].values()
        ):
            return JSONResponse({"success": False, "result": "Incorrect"})
    return JSONResponse({"success": True, "result": "Correct"})


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
