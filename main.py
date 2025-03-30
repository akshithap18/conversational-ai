from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, send_file, send_from_directory
import threading
import os
import vertexai
import base64
from vertexai.generative_models import GenerativeModel, Part
import json

import os

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

project_id = os.environ.get('project_id')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

prompt = """
Please provide an exact trascript for the audio, followed by sentiment analysis.

Your response should follow the format (json):

Text: USERS SPEECH TRANSCRIPTION

Sentiment Analysis: positive|neutral|negative

Sentiment Score : -1 to 1
"""

vertexai.init(project=project_id, location="us-central1")
model = GenerativeModel("gemini-1.5-flash-001")

def audio_to_text(audio_file_path):
    try:
        with open(audio_file_path, "rb") as audio_file:
            audio_data = audio_file.read()
            audio_part = Part.from_data(data=audio_data, mime_type="audio/wav")
            prompt_part = Part.from_text(prompt)
            response = model.generate_content([audio_part, prompt_part])
            clean_response = response.text.replace('```json', '').replace('```', '').strip()
            txt_file_path = audio_file_path + ".txt"
            with open(txt_file_path, "w") as text_file:
                text_file.write(clean_response)
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_files(dir_path):
    files = []
    for filename in os.listdir(dir_path):
        if allowed_file(filename):
            files.append(filename)
    files.sort(reverse=True)
    return files

@app.route('/')
def index():
    files = get_files(UPLOAD_FOLDER)
    tts_files = get_files(TTS_FOLDER)
    return render_template('index.html', files=files,tts_files=tts_files)

@app.route('/upload', methods=['POST'])
def upload_audio():
    if 'audio_data' not in request.files:
        flash('No audio data')
        return redirect(request.url)
    file = request.files['audio_data']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file:

        filename = datetime.now().strftime("%Y%m%d-%I%M%S%p") + '.wav'
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        # Start processing the audio file in a background thread
        threading.Thread(target=audio_to_text, args=(file_path,)).start()

    return redirect('/') #success

@app.route('/upload/<filename>')
def get_file(filename):
    return send_file(filename)


@app.route('/script.js',methods=['GET'])
def scripts_js():
    return send_file('./script.js')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)

