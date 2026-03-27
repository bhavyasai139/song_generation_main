# AI Song Generation & Voice Synthesis – Multimodal Music Generation System

## Overview
This project is a multimodal AI system that converts voice input into a complete song by analyzing emotion and generating lyrics, vocals, and background music. It integrates audio processing, deep learning, and generative AI to produce mood-aligned music outputs.

## Features
- Classifies music genres using CNN trained on the GTZAN dataset  
- Extracts audio features such as MFCCs and spectrograms using Librosa  
- Performs speech-based emotion recognition using audio features  
- Generates lyrics using LLM-based text emotion analysis  
- Synthesizes vocals using Bark neural voice model  
- Generates background music using MusicGen  
- Applies audio processing techniques for improved output quality  

## System Architecture
The system is composed of multiple stages:

1. Audio Processing Layer – Extracts features and analyzes input audio  
2. Emotion Analysis Layer – Detects emotion from speech and text  
3. Generation Layer – Produces lyrics, vocals, and background music  
4. Post-processing Layer – Enhances audio quality and combines outputs  

## How It Works
1. Input voice/audio prompt  
2. Extract audio features using Librosa  
3. Perform emotion detection from speech  
4. Generate lyrics based on detected emotion  
5. Convert lyrics into vocals using Bark  
6. Generate background music using MusicGen  
7. Apply audio enhancements (pitch shifting, time-stretching, normalization)  
8. Combine outputs to produce final song  

## Tech Stack

### AI / ML
- TensorFlow / Keras  
- CNN (for genre classification)  
- Bark (voice synthesis)  
- MusicGen (music generation)  

### Audio Processing
- Librosa (MFCC, spectrograms, feature extraction)  

### NLP / LLM
- LLM-based text emotion analysis  

### Tools
- Python  
- Jupyter Notebook  

## Installation and Setup

### 1. Clone the repository
git clone https://github.com/bhavyasai139/song_generation_main.git
cd song_generation_main

### 2. Install dependencies
pip install -r requirements.txt

### 3. Run the project
python main.py

## Demo / Screenshots
Add screenshots or a demo audio/video link here.

## Future Improvements
- Improve emotion detection accuracy  
- Enhance music quality with advanced models  
- Add real-time song generation support  
- Deploy as a web-based application  

## Contact
GitHub: https://github.com/bhavyasai139  
LinkedIn: https://www.linkedin.com/in/gadikota-bhavya-sai  
