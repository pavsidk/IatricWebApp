from flask import Flask, render_template, request, jsonify
import os
import tempfile
from groq import Groq
from verify import *

app = Flask(__name__)

TRANSCRIPTS = []
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def transcribe_audio(audio_chunk: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_audio:
        temp_audio.write(audio_chunk)
        temp_audio.flush()

        with open(temp_audio.name, "rb") as f:
            translation = client.audio.translations.create(
                file=(temp_audio.name, f),
                model="whisper-large-v3",
                prompt="use clinical terminology and correct spelling for conditions, medications, and procedures in a medical context",
                response_format="json",
                temperature=0.0 
            )

        print(translation.text)
        TRANSCRIPTS.append(translation.text)
        return translation.text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    audio = request.files['audio']
    audio.save('recorded.wav')
    with open("recorded.wav", "rb") as f:
        audio_bytes = f.read()
    
    
    transcript = transcribe_audio(audio_bytes)
    # This is your placeholder function


    result = generate_validation(transcript)
    return jsonify({
        "transcript": transcript,
        "claim": result.get("claim", ""),
        "validity": result.get("validity", None),
        "question": result.get("question", ""),
        "sources": result.get("sources", [])
    })


def validate_claim(audio_path):
    # TODO: Replace with real claim validation logic
    return "Received and processed: " + audio_path

if __name__ == '__main__':
    app.run(debug=True)
