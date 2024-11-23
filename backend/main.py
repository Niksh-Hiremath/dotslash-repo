from flask import Flask, request, jsonify
import whisper
import openai
import os

app = Flask(_name_)

# Load Whisper model
model = whisper.load_model("base")

# Set OpenAI API Key
openai.api_key = "YOUR_OPENAI_API_KEY"

@app.route("/upload", methods=["POST"])
def upload_audio():
    # Save the uploaded audio file
    if "audio" not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    audio_file = request.files["audio"]
    file_path = os.path.join("uploads", audio_file.filename)
    audio_file.save(file_path)

    # Transcribe the audio using Whisper
    result = model.transcribe(file_path)
    transcription = result["text"]
    print("Transcription:", transcription)

    # Send transcription to ChatGPT
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": transcription}]
    )
    chatgpt_response = response["choices"][0]["message"]["content"]
    print("ChatGPT Response:", chatgpt_response)

    # Send the response back to the frontend
    return jsonify({"transcription": transcription, "chatgpt_response": chatgpt_response})

if _name_ == "_main_":
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)