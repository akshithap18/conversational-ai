# Speech-to-Text and Text-to-Speech Flask Application

This is a Flask web application that allows users to upload audio files for transcription (speech-to-text) and text data to generate speech (text-to-speech). It integrates with Google Cloud's Text-to-Speech and Speech-to-Text APIs to process the files asynchronously.

## Features

- **Upload Audio Files**: Users can upload audio files (WAV format), and the app will transcribe the speech to text.
- **Upload Text**: Users can provide text, and the app will generate speech (WAV format).
- **Asynchronous Processing**: All audio transcription and text-to-speech processing happens in the background, ensuring the app remains responsive.
- **File Management**: Users can view and download both transcribed text and audio files.

## Requirements

- Python 3.x
- Google Cloud account with enabled Text-to-Speech and Speech-to-Text APIs
- Flask
- Google Cloud client libraries

## Installation

### Step 1: Clone the repository

```bash
git clone https://github.com/yourusername/speech-to-text-flask.git
cd speech-to-text-flask
```

### Step 2: Set up a Python virtual environment (optional but recommended)

```bash
python -m venv venv
source venv/bin/activat
```

### Step 3: Install required Python libraries

```bash
pip install -r requirements.txt
```

### Step 4: Google Cloud Setup
- Ensure that you have a Google Cloud account and the Speech-to-Text and Text-to-Speech APIs are enabled.
- Set up a service account and download the credentials JSON file.
- Set the environment variable for Google Cloud credentials:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials-file.json"  # On Windows use set
```

### Step 5: Running the Flask Application
```bash
python app.py
```

The Flask app will run locally, and you can access it in your browser at http://127.0.0.1:5000/

### API Endpoints
- GET /: Displays the homepage with uploaded audio files and generated text-to-speech files.
- POST /upload: Upload an audio file (WAV format) for transcription.
- POST /upload_text: Submit text data to generate speech.
- GET /upload/<filename>: Get the uploaded audio file.
- GET /uploads/<filename>: Access a specific uploaded audio file.
- GET /tts_uploads/<filename>: Access a generated text-to-speech file.

