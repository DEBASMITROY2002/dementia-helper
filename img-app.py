from flask import Flask, send_from_directory
import os

app = Flask(__name__)

MEM_IMAGE_FOLDER = "./data/mems/imgs"

@app.route('/data/mems/imgs/<filename>')
def serve_image(filename):
    try:
        return send_from_directory(MEM_IMAGE_FOLDER, filename)
    except Exception as e:
        return f"Error: {str(e)}", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)