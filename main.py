from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, send_file, send_from_directory
from google.cloud import texttospeech_v1
from google.cloud import speech
import threading

import os

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
TTS_FOLDER = 'tts'
ALLOWED_EXTENSIONS = {'wav'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TTS_FOLDER'] = TTS_FOLDER
client_options = {"api_key": "AIzaSyBphC526Gbx2P1nOoQerguLuY-VNLq_lqM"}


client_texttospeech=texttospeech_v1.TextToSpeechClient(client_options=client_options)

client_speechtotext=speech.SpeechClient(client_options=client_options)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TTS_FOLDER, exist_ok=True)

def speech_to_text(content):
  audio=speech.RecognitionAudio(content=content)
  config=speech.RecognitionConfig(language_code="en-US",model="latest_long",audio_channel_count=1,enable_word_confidence=True,enable_word_time_offsets=True)
  operation=client_speechtotext.long_running_recognize(config=config, audio=audio)
  response=operation.result(timeout=90)
  txt = ''
  for result in response.results:
    txt = txt + result.alternatives[0].transcript + '\n'
  return txt

def text_to_speech(text):
    input = texttospeech_v1.SynthesisInput(text = text)
    voice = texttospeech_v1.VoiceSelectionParams(language_code = "en-UK",ssml_gender = "MALE")
    audio_config = texttospeech_v1.AudioConfig(audio_encoding = "LINEAR16")
    request = texttospeech_v1.SynthesizeSpeechRequest(input=input,voice=voice,audio_config=audio_config)
    response = client_texttospeech.synthesize_speech(request=request)
    return response.audio_content

def process_text_and_save_files(text,file_path):
    # Process the text and generate the files in a background thread
    wav = text_to_speech(text)

    with open(file_path, 'wb') as f:
        f.write(wav)

def process_audio_and_save_files(file_path):
    # Process the audio file and save the transcribed text in the background
    with open(file_path, 'rb') as f:
        data = f.read()

    text = speech_to_text(data)

    txt_file_path = file_path + ".txt"
    with open(txt_file_path, "w") as text_file:
        text_file.write(text)

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
        threading.Thread(target=process_audio_and_save_files, args=(file_path,)).start()

    return redirect('/') #success

@app.route('/upload/<filename>')
def get_file(filename):
    return send_file(filename)

    
@app.route('/upload_text', methods=['POST'])
def upload_text():
    text = request.form['text']

    filename = datetime.now().strftime("%Y%m%d-%I%M%S%p") + '.wav'
    file_path = os.path.join(app.config['TTS_FOLDER'], filename)

    with open(file_path + ".txt" , "w") as file:
        file.write(text)

    process_text_and_save_files(text,file_path)    

    #threading.Thread(target=process_text_and_save_files, args=(text,file_path,)).start()

    return redirect('/') #success

@app.route('/script.js',methods=['GET'])
def scripts_js():
    return send_file('./script.js')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/tts_uploads/<filename>')
def tts_uploaded_file(filename):
    return send_from_directory(app.config['TTS_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)