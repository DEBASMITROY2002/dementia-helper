from flask import Flask, request, jsonify
import os
import speech_recognition as sr
from gtts import gTTS
import base64
import random

app = Flask(__name__)
GLOBAL_CONFIG = {}

# Helper function for transcribing audio to text
def transcribe_audio(audio_file_path):
    try:
        r = sr.Recognizer()
        with sr.AudioFile(audio_file_path) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data)
        return {'transcribed_text': text}, 200
    except Exception as e:
        return {'error': str(e)}, 500

# Helper function for generating audio from text
def generate_audio_answer(text, language, output_file_path):
    try:
        tts = gTTS(text=text, lang=language)
        tts.save(output_file_path)

        # Check if file was created
        if os.path.exists(output_file_path):
            return {'message': 'Audio generated successfully', 'output_file': output_file_path}, 200
        else:
            return {'error': 'Failed to generate audio'}, 500
    except Exception as e:
        return {'error': str(e)}, 500
    
def iniatlize_config():
    GLOBAL_CONFIG['data_folder'] = "./data"
    GLOBAL_CONFIG['upload_folder'] = f"{GLOBAL_CONFIG['data_folder']}/uploads"
    GLOBAL_CONFIG['processed_folder'] = f"{GLOBAL_CONFIG['data_folder']}/processed"
    GLOBAL_CONFIG['audio_upload_folder'] = f"{GLOBAL_CONFIG['upload_folder']}/audio"
    GLOBAL_CONFIG['image_upload_folder'] = f"{GLOBAL_CONFIG['upload_folder']}/image"
    GLOBAL_CONFIG['audio_processed_folder'] = f"{GLOBAL_CONFIG['processed_folder']}/audio"
    GLOBAL_CONFIG['image_processed_folder'] = f"{GLOBAL_CONFIG['processed_folder']}/image"

    for key in GLOBAL_CONFIG:
        if 'folder' in key:
            if not os.path.exists(GLOBAL_CONFIG[key]):
                os.makedirs(GLOBAL_CONFIG[key])


def temp_processing(text, img = False):
    try:
        if "key" in text:
            return "Probably you are talking about the key to the door. You have left it on the table in the drawin room at around 10:00 AM"
        if "water" in text:
            return "You drank water at around 30 minutes ago. You should drink water again after 1 hour"
    except Exception as e:
        return None
    if img == True:
        return "This is a picture of your dad. his name is Jack. He used to love your pet Nook. He used to play with him a lot."
    return None

@app.route('/query-input', methods=['POST'])
def process_input():
    try:
        user_id = request.form.get('user_id')
        time_stamp = request.form.get('time_stamp')
        input_text = request.form.get('input_text',"")
        audio_file = request.files.get('audio')
        image_file = request.files.get('image')
        language = request.form.get('language', 'en')

        # Saving the request data
        if audio_file:
            # Save the audio file
            audio_file_path = f"{GLOBAL_CONFIG['audio_upload_folder']}/{user_id}.wav"
            audio_file.save(audio_file_path)

        if image_file:
            # Save the image file
            image_file_path = f"{GLOBAL_CONFIG['image_upload_folder']}/{user_id}.png"
            image_file.save(image_file_path)

        audio_text = ""
        output_audio = None
        encoded_output_audio = None

        # Process the input
        if audio_file:
            audio_text = transcribe_audio(audio_file_path)[0].get('transcribed_text')
            print("audio_text ----> ", audio_text)
        
        total_text = f"{input_text} {audio_text}"
        output_text = temp_processing(total_text, img = image_file is not None)
        encoded_output_audio = None

        if output_text:
            outut_processed_path = f"{GLOBAL_CONFIG['audio_processed_folder']}/{user_id}.wav"
            output_audio = generate_audio_answer(input_text, 
                                                 language, 
                                                 outut_processed_path)
            # # base64 encode the audio file"
            with open(outut_processed_path, "rb") as audio:
                encoded_output_audio = base64.b64encode(audio.read()).decode('utf-8')
            
        # Response
        response = {
            'user_id': user_id,
            'output_text': output_text,
            'output_audio': encoded_output_audio
        }

        return jsonify(response), 200

    except Exception as e:
        return {'error': str(e)}, 500


IMG_TEXT_PAIR = []

@app.route('/create-memory', methods=['POST'])
def create_imgs_text_pair():
    try:
        user_id = request.form.get('user_id')
        input_text = request.form.get('input_text')
        image_file = request.files.get('image')

        if image_file:
            # Save the image file
            image_file_path = f"{GLOBAL_CONFIG['image_upload_folder']}/{user_id}.png"
            image_file.save(image_file_path)
        
        if input_text:
            IMG_TEXT_PAIR.append({'user_id': user_id, 'input_text': input_text, 'image_path': image_file_path})

        return {'message': 'Image-Text pair created successfully'}, 200

    except Exception as e:
        return {'error': str(e)}, 500
        
EVENTS = []

@app.route('/create-event', methods=['POST'])
def create_event():
    try:
        user_id = request.form.get('user_id')
        time_stamp = request.form.get('time_stamp')
        location = request.form.get('location') # sample [0.1,33.3,2.2]
        event_id = random.randint(1,1000)
        image_file = request.files.get('image')
        audio_file = request.files.get('audio')
        
        # processing code
        EVENTS.append(
            {
                'user_id': user_id, 
                'time_stamp': time_stamp, 
                'location': location, 
                'event_id': event_id
             }
            )
        
        return {'message': 'Event created successfully'}, 200

    except Exception as e:
        return {'error': str(e)}, 500
        



if __name__ == '__main__':
    iniatlize_config()
    app.run(debug=True,port=8080,host='0.0.0.0')
