from prediction import enroll, recognize

from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import tempfile
import prediction
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app,resources={r"/*": {"origins": "*"}})

# Set maximum file size for uploads to 16 megabytes
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Set upload folder and allowed extensions for file uploads
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['ALLOWED_EXTENSIONS'] = {'wav', 'flac','webm','ogg'}

def allowed_file(filename):
    """Check if a file has an allowed extension
    inputs: str (filename)
    outputs: bool"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


from pydub import AudioSegment

@app.route('/enroll', methods=['POST'])
def enroll():
    """Enroll a user with an audio file
    inputs: str (Name of the person to be enrolled and registered)
            file (Audio file of the person to enroll in .webm format)
    outputs: None"""

    # Check if the name and audio file are included in the request
    if 'name' not in request.form or 'audio' not in request.files:
        return jsonify({'error': 'Name and audio file are required.'}), 400

    name = request.form['name']
    audio_file = request.files['audio']

    # Check if the file has an allowed extension
    if not allowed_file(audio_file.filename):
        return jsonify({'error': 'Audio file must be in WAV or FLAC format.'}), 400
    
    # Save the audio file to the server
    audio_filename = secure_filename(name) + '.' + audio_file.filename.rsplit('.', 1)[1].lower()
    audio_file.save(os.path.join(app.config['UPLOAD_FOLDER'], audio_filename))


    # Convert the audio file to WAV format
    import moviepy.editor as moviepy
    audio_filename2 = audio_filename.replace(".webm",".wav")
    audio_filename2 = audio_filename.replace(".ogg",".wav")

    audio = AudioSegment.from_file(os.path.join(app.config['UPLOAD_FOLDER'], audio_filename))
    audio.export(os.path.join(app.config['UPLOAD_FOLDER'], audio_filename2), format="wav")

    

    print(os.path.join(app.config['UPLOAD_FOLDER'], audio_filename2))
    # Enroll the user with the audio file
    result = prediction.enroll(name, os.path.join(app.config['UPLOAD_FOLDER'], audio_filename2))
    print(result)

    return jsonify({'result': result})



@app.route('/recognize', methods=['POST'])
def recognize():

    # Check if the audio file is included in the request
    if 'audio' not in request.files:
        return jsonify({'error': 'Audio file is required.'}), 400
    
    name = request.form['name']
    audio_file = request.files['audio']
    
    # Check if the file has an allowed extension
    if not allowed_file(audio_file.filename):
        return jsonify({'error': 'Audio file must be in WAV or FLAC format.'}), 400
    
    # Save the audio file to the server
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        audio_filename = temp.name + '.' + audio_file.filename.rsplit('.', 1)[1].lower()
        audio_file.save(audio_filename)
    
    # Recognize the user with the audio file
    result = prediction.recognize(audio_filename)
    
    os.remove(audio_filename)  # Delete the temporary audio file
    print(result['Recognized'])
    if result['Recognized'] == name:
        return jsonify({'result': "Success", 'name': result}),200
    else:
        return jsonify({'result': "Unauthorized"}),401
    






if __name__ == "__main__":
    app.run()
