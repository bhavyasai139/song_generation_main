from flask import Flask, request, jsonify
from flask_cors import CORS
from quart import Quart, request, jsonify
from quart_cors import cors
import os
from pydub import AudioSegment
from rich.console import Console
import tensorflow as tf
import numpy as np
import librosa
import cv2
import asyncio
import base64

# Initialize the Quart app
app = Quart(__name__)
app = cors(app, allow_origin="http://127.0.0.1:8000")
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

# Initialize console for logging
console = Console()

# Load model and classes
classes = ['classical', 'jazz', 'pop', 'rock']
model_path = os.path.join(os.getcwd(), 'model.h5')
console.log("Loading the model...")
model = tf.keras.models.load_model(model_path)
console.log("Model loaded successfully!")

# Function to load and preprocess audio data
async def load_and_preprocess_data(file_path, start_time, duration, target_shape=(150, 150)):
    return await asyncio.to_thread(_sync_load_and_preprocess_data, file_path, start_time, duration, target_shape)

def _sync_load_and_preprocess_data(file_path, start_time, duration, target_shape):
    data = []
    
    # Load audio data with specified start time and duration
    audio_data, sample_rate = librosa.load(file_path, sr=None, offset=start_time, duration=duration)
    console.log(f"Loaded audio from {start_time}s to {start_time + duration}s.")
    
    chunk_duration = 4  # seconds
    overlap_duration = 2  # seconds
    chunk_samples = int(chunk_duration * sample_rate)
    overlap_samples = int(overlap_duration * sample_rate)
    num_chunks = int(np.ceil((len(audio_data) - chunk_samples) / (chunk_samples - overlap_samples)))

    for i in range(max(num_chunks, 1)):  # Ensure at least one chunk
        start = i * (chunk_samples - overlap_samples)
        end = start + chunk_samples
        if end > len(audio_data):
            break
        chunk = audio_data[start:end]
        mel_spectrogram = librosa.feature.melspectrogram(y=chunk, sr=sample_rate)
        mel_spectrogram = cv2.resize(mel_spectrogram, target_shape, interpolation=cv2.INTER_LINEAR)
        data.append(mel_spectrogram)

    return np.array(data)

# Function to perform model prediction
async def model_prediction(X_test):
    return await asyncio.to_thread(_sync_model_prediction, X_test)

def _sync_model_prediction(X_test):
    y_pred = model.predict(X_test)
    predicted_categories = np.argmax(y_pred, axis=1)
    unique_elements, counts = np.unique(predicted_categories, return_counts=True)
    max_count = np.max(counts)
    max_elements = unique_elements[counts == max_count]
    return max_elements[0]

# Final prediction function
# async def final_model_prediction(file_path_2, start_time, duration):
#     console.log(f"Processing file: {file_path_2}")
#     file_path = file_path_2
#     temp_file_path = "temp.wav"

#     if not os.path.exists(file_path):
#         console.log(f"Error: File not found at {file_path}")
#         return None

#     # Convert to WAV format
#     await asyncio.to_thread(AudioSegment.from_mp3(file_path).export, temp_file_path, format="wav")

#     # Load and preprocess data
#     X_test = await load_and_preprocess_data(temp_file_path, start_time, duration)

#     # Perform prediction
#     c_index = await model_prediction(X_test)
#     return classes[c_index]

async def final_model_prediction(file_path_2, start_time, duration):
    print(f"Processing file: {file_path_2}")
    file_path = file_path_2
    temp_file_path = "temp.wav"

    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return None

    try:
        # Load the audio file asynchronously
        audio = await asyncio.to_thread(AudioSegment.from_file, file_path)
        
        # Export the processed audio
        await asyncio.to_thread(audio.export, temp_file_path, format="wav")
        print("Audio processing completed successfully.")
        
    except Exception as e:
        print(f"An error occurred: {e}")

    # Load and preprocess data
    X_test = await load_and_preprocess_data(temp_file_path, start_time, duration)

    # Perform prediction
    c_index = await model_prediction(X_test)
    return classes[c_index]


@app.route('/process', methods=['POST'])
async def process_data():
    # Extract query parameters
    data = await request.get_json()
    filename = data.get("filename")
    content_type = data.get("content_type")
    audio_data = data.get("audio_data")
    start_time = float(data.get('start', 0))
    end_time = float(data.get('end', 0))
    # file_name = request.args.get('fileName', "")
    if not all([filename, content_type, audio_data]):
            return jsonify({"error": "Missing required parameters"}), 400

        # Decode and save audio data
    audio_bytes = base64.b64decode(audio_data)
    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", filename)

    with open(file_path, "wb") as f:
        f.write(audio_bytes)
    # Validate duration
    duration = end_time - start_time
    if duration < 40:
        message = "40secs"
    elif 40 <= duration < 60:
        message = "60secs"
    elif 60 <= duration < 80:
        message = "80secs"
    elif 80 <= duration < 100:
        message = "100secs"
    else:
        message = "Duration exceeds allowed range."

    # Perform prediction
    # file_path = os.path.join(os.getcwd(), filename)
    output = await final_model_prediction(file_path, start_time, duration)

    return jsonify({"message": message, "output": output})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
