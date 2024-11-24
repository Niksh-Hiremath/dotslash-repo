from fastapi import APIRouter, Header, HTTPException, UploadFile, File, Body
from fastapi.responses import JSONResponse
from typing import Annotated
import os
from dotenv import load_dotenv
from pathlib import Path
from uuid import uuid4
import whisper
import openai
import json
import textwrap
# from RestrictedPython import compile_restricted
# from RestrictedPython import safe_globals

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

with open("prompt.txt", "r") as f:
    PROMPT = f.read()


async def check_leetcode_solution(
    code: str, func: str, solutions: list, *input: list
) -> bool:
    try:
        # compiled_code = compile_restricted(code, "<string>", "exec")
        # local_vars = {}
        # exec(compiled_code, safe_globals, local_vars)

        # print("Local Vars:", local_vars)
        # if "Solution" in local_vars and hasattr(local_vars["Solution"], func):
        #     result = getattr(local_vars["Solution"](), func)(*input)
        #     print("Result:", result)
        #     if result in solutions:
        #         return True
        # return False
        loc = {}
        code = f"async def func():\n{textwrap.indent(code, '  ')}\n\n  sol = Solution().{func}({','.join(map(str, input))})\n  return sol in {solutions}"
        result = exec(code, loc)
        func = loc["func"]
        result = await func()
        if result is True:
            return True
        return False
    except Exception:
        return False


@router.post("/check-code")
async def check_code(
    authorization=Header(..., alias="Authorization"),
    question_id=Body(..., alias="QuestionId"),
    code=Body(..., alias="code"),
):
    if authorization != AUTHORIZATION_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    func = SOLUTIONS[question_id]["function"]
    for testcase in SOLUTIONS[question_id]["testcases"]:
        if not (
            await check_leetcode_solution(
                code, func, testcase["solutions"], *testcase["input"].values()
            )
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
        file_path = UPLOAD_DIR / f"{uuid4()}-{audio.filename}"
        with open(file_path, "wb") as f:
            f.write(await audio.read())

        # Transcribe the audio using Whisper
        result = model.transcribe(str(file_path))
        transcription = result["text"]
        print("Transcription:", transcription)

        # Send transcription to ChatGPT
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": transcription},
            ],
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
