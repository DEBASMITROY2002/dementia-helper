# !pip install text-to-speech SpeechRecognition pydub

from flask import Flask, request, jsonify
import speech_recognition as sr
from text_to_speech import save
import os

app = Flask(__name__)

# Endpoint to transcribe audio to text
@app.route('/transcribe_audio', methods=['POST'])
def transcribe_audio():
    if 'audio_file' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio_file']
    
    try:
        r = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data)
        return jsonify({'transcribed_text': text}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to generate speech from text
@app.route('/generate_audio_answer', methods=['POST'])
def generate_audio_answer():
    data = request.get_json()
    
    if not data or 'text' not in data or 'language' not in data or 'output_file' not in data:
        return jsonify({'error': 'Please provide text, language, and output_file in the request'}), 400

    text = data['text']
    language = data['language']
    output_file = data['output_file']

    try:
        # Generate audio from text
        save(text, language, file=output_file)
        
        # Verify if the output file was created
        if os.path.exists(output_file):
            return jsonify({'message': 'Audio generated successfully', 'output_file': output_file}), 200
        else:
            return jsonify({'error': 'Failed to generate audio'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
