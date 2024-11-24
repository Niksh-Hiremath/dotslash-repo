from fastapi import APIRouter, Header, HTTPException, File, Body
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from pathlib import Path
from uuid import uuid4
import whisper
import openai
import json
import textwrap
import numpy as np
from pyAudioAnalysis import audioBasicIO
from pyAudioAnalysis import ShortTermFeatures

load_dotenv()

AUTHORIZATION_KEY = os.getenv("AUTHORIZATION_KEY")

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

router = APIRouter()

model = whisper.load_model("base")

openai.api_key = os.getenv("OPENAI_API_KEY")


client = openai.OpenAI()

SESSIONS = {}

with open("solutions.json", "r") as f:
    SOLUTIONS = json.load(f)

with open("prompt.txt", "r") as f:
    PROMPT = f.read()

SYSTEM_MESSAGE = {"role": "system", "content": PROMPT}

with open("prompt_summary.txt", "r") as f:
    PROMPT_SUMMARY = f.read()

SUMMARY_MESSAGE = {"role": "system", "content": PROMPT_SUMMARY}


async def check_leetcode_solution(
    code: str, func: str, solutions: list, *input: list
) -> bool:
    try:
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


def send_chatgpt(messages: list):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            SYSTEM_MESSAGE,
            *messages,
        ],
    )
    return response["choices"][0]["message"]["content"]


def get_summary(messages: list):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            SYSTEM_MESSAGE,
            *messages,
            SUMMARY_MESSAGE,
        ],
    )
    return response["choices"][0]["message"]["content"]


def transcribe(path):
    audio_file = open(path, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1", file=audio_file, response_format="text"
    )
    return transcription


def audio_analysis(path):
    """Returns avg_fluency, avg_pausing"""
    # Load the audio file
    audio_path = path
    [Fs, x] = audioBasicIO.read_audio_file(
        audio_path
    )  # Fs: Sampling rate, x: Audio signal

    # Convert to mono if the audio is stereo
    if x.ndim > 1:
        x = x.mean(axis=1)

    # Step size (25ms) and window size (50ms)
    step_size = int(0.025 * Fs)  # Convert from seconds to samples
    window_size = int(0.05 * Fs)  # Convert from seconds to samples

    # Extract short-term features
    F, feature_names = ShortTermFeatures.feature_extraction(
        x, Fs, window_size, step_size
    )

    # Extract specific features for further analysis
    energy = F[1]  # Short-term Energy
    zcr = F[0]  # Zero-Crossing Rate

    # Set a silence threshold based on energy
    silence_threshold = 0.05 * np.max(energy)  # 10% of max energy

    # Detect pauses (regions where energy is below the threshold)
    pauses = np.where(energy < silence_threshold, 1, 0)

    # Calculate the total pause duration
    total_pause_duration = np.sum(pauses) * (step_size / Fs)

    # Calculate average ZCR for voiced regions (where energy > silence threshold)
    voiced_regions = energy > silence_threshold
    average_zcr = np.mean(zcr[voiced_regions])

    # Define the ideal range for ZCR
    zcr_ideal_min = 0.01
    zcr_ideal_max = 0.1

    # Score calculation for ZCR
    if average_zcr < zcr_ideal_min:
        zcr_score = 100  # Perfect score for low ZCR
    elif average_zcr > zcr_ideal_max:
        zcr_score = 0  # Poor score for high ZCR
    else:
        zcr_score = 100 * (
            1 - (average_zcr - zcr_ideal_min) / (zcr_ideal_max - zcr_ideal_min)
        )

    total_speech_duration = (
        len(x) / Fs
    )  # Length of audio signal divided by sampling rate

    # Define the ideal range for pause percentage
    pause_ideal_min = 0  # No pauses
    pause_ideal_max = 100  # shit speech
    pause_time_percentage = (1 - total_pause_duration / total_speech_duration) * 100

    # Score calculation for pause percentage
    if pause_time_percentage < pause_ideal_min:
        pause_score = 100  # Perfect score for no pauses
    elif pause_time_percentage > pause_ideal_max:
        pause_score = 0  # Poor score for too many pauses
    else:
        pause_score = 100 * (
            1
            - (pause_time_percentage - pause_ideal_min)
            / (pause_ideal_max - pause_ideal_min)
        )

    return zcr_score, pause_score


@router.post("/chat")
async def upload_audio(
    authorization=Header(..., alias="Authorization"),
    audio=File(...),
    session_id=Body(None, alias="SessionId"),
):
    if authorization != AUTHORIZATION_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        # Save the uploaded audio file
        file_path = UPLOAD_DIR / f"{uuid4()}-{audio.filename}"
        with open(file_path, "wb") as f:
            f.write(await audio.read())

        if session_id is None:
            session_id = str(uuid4())

        if session_id not in SESSIONS:
            # Analyze the audio using pyAudioAnalysis
            avg_fluency, avg_pausing = audio_analysis(file_path)

            SESSIONS[session_id] = {
                "avg_fluency": avg_fluency,
                "avg_pausing": avg_pausing,
                "messages": [],
            }

        # Transcribe the audio using Whisper
        transcription = transcribe(file_path)

        user_message = {"role": "user", "content": transcription}
        SESSIONS[session_id]["messages"].append(user_message)

        # Send the messages to ChatGPT
        response = send_chatgpt(SESSIONS[session_id])
        SESSIONS[session_id]["messages"].append({"role": "system", "content": response})

        # Delete the file after processing
        # try:
        #     os.remove(file_path)
        # except FileNotFoundError:
        #     pass

        if len(SESSIONS[session_id]["messages"]) > 5:
            results = get_summary(SESSIONS[session_id])
            return JSONResponse(
                {
                    "success": True,
                    "session_id": session_id,
                    "transcription": transcription,
                    "response": response,
                    "summary": results,
                }
            )

        return JSONResponse(
            {
                "success": True,
                "session_id": session_id,
                "transcription": transcription,
                "response": response,
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
