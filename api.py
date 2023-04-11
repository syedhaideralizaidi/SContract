# from flask import Flask, request, jsonify
# import os
# import whisper

# app = Flask(__name__)

# @app.route('/transcribe', methods=['POST'])
# def transcribe():
#     # Get the audio file from the request
#     file = request.files['audio']
#     if not file:
#         return jsonify({'error': 'Audio file not found'}), 400

#     # Read the audio file into memory
#     audio_bytes = file.read()

#     # Initialize the Whisper API client with your API key
#     client = whisper.Client(os.environ.get('WHISPER_API_KEY'))

#     # Call the transcribe method with the audio bytes and the desired output format (text)
#     transcription, err = client.transcribe(audio_bytes, whisper.Output.TEXT)
#     if err:
#         return jsonify({'error': 'Transcription failed'}), 500

#     # Return the transcription as the response
#     return jsonify({'transcription': transcription}), 200

# if __name__ == '__main__':
#     app.run(debug=True, port=8080)


# import subprocess
# import whisper
# model = whisper.load_model("base")

# video_in = 'file.wav'
# audio_out = 'audio.mp3'

# ffmpeg_cmd = f"ffmpeg -i {video_in} -vn -c:a libmp3lame -b:a 192k {audio_out}"

# subprocess.run(["ffmpeg", "-i", video_in, "-vn", "-c:a", "libmp3lame", "-b:a", "192k", audio_out])

# result = model.transcribe(audio_out)
# print(result["text"])


from flask import Flask, request, jsonify
import whisper
import spacy
import string
import tempfile
import subprocess

def filter_type(doc):
    entities = [ent for ent in doc.ents if ent.label_ == "TYPE"]
    extracted = []

    for entity in entities:
        extracted.append(entity)

    new_extracted = []
    table = str.maketrans("", "", string.punctuation)
    for entity in extracted:
        filtered_text = entity.text.translate(table)
        new_extracted.append(filtered_text)

    for extract in new_extracted:
        if extract=='apartment' or extract=='Apartment' or extract=='rent' or extract=='renting' or extract=='rental':
            filter1 = 'rental'
            return filter1
        elif extract=='selling' or extract=='sell' or extract=='buying' or extract=='buy' or extract=='sale' or extract=='purchasing':
            filter1 = 'sale/purchase'
            return filter1


model = whisper.load_model("base")
nlp1 = spacy.load(r"model-last") #load the best model

app = Flask(__name__)

@app.route('/', methods=['POST'])
def transcribe_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No audio file found in request'}), 400

    audio_file = request.files['file']
    # audio_out = 'audio.mp3'
    # ffmpeg_cmd = f"ffmpeg -i {audio_file} -vn -c:a libmp3lame -b:a 192k {audio_out}"
    # subprocess.run(["ffmpeg", "-i", audio_file, "-vn", "-c:a", "libmp3lame", "-b:a", "192k", audio_out])
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        audio_file.save(tmp_file.name)
        audio_out = 'audio.mp3'
        ffmpeg_cmd = f"ffmpeg -i {tmp_file.name} -vn -c:a libmp3lame -b:a 192k {audio_out}"
        subprocess.run(ffmpeg_cmd.split())

    result = model.transcribe(audio_out)
    doc = nlp1(result['text'])
    entity_array = {}

    for ent in doc.ents:
        entity_array[ent.text] = ent.label_

    filter1 = filter_type(doc)

    return jsonify({'text': result['text'], 'filter':filter1, 'entities':entity_array}), 200

if __name__ == '__main__':
    app.run(debug=True)
