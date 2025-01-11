from flask import Flask, request, jsonify, render_template
import assemblyai as aai
import os
import json
from datetime import datetime
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch

app = Flask(__name__)

# Set AssemblyAI API key
aai.settings.api_key = "2d087d1a84444b13bf433655d8bb0c55"

# Ensure uploads and JSON folder exists
os.makedirs("uploads", exist_ok=True)
os.makedirs("data", exist_ok=True)

# Initialize the client with the API key
client = genai.Client(api_key="AIzaSyAY9jdBUpmOGf6X6kgCpw378Dss5mnQ8E0")

# Define the model ID
model_id = "gemini-2.0-flash-exp"

# Initialize the Google Search tool
google_search_tool = Tool(
    google_search=GoogleSearch()
)

@app.route("/")
def meeting():
    # Get the username from query parameters
    username = request.args.get("username", "Aman Raut")
    return render_template("meeting.html", username=username)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    # Save the uploaded file temporarily
    audio_file = request.files['audio']
    username = request.form.get('username', 'Unknown')  # Get the username from the form data or use 'Unknown'
    temp_path = "uploads/meeting_audio.wav"
    audio_file.save(temp_path)
    
    # Transcribe the audio
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(temp_path)
    
    # Get the current date and time
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")  # Format as YYYY-MM-DD
    time = now.strftime("%H:%M:%S")  # Format as HH:MM:SS
    
    # Define the JSON file path
    json_path = "data/transcriptions.json"
    
    # Load existing data from the JSON file, or initialize an empty list if the file does not exist
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            data = json.load(f)
    else:
        data = []
    
    # Create a new entry
    new_entry = {
        "Username": username,
        "Date": date,
        "Time": time,
        "Transcription": transcript.text
    }
    
    # Append the new entry to the data
    data.append(new_entry)
    
    # Save the updated data back to the JSON file
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=4)
    
    print(transcript.text)
    return jsonify({'text': transcript.text})

def generate_summary(transcription):
    response = client.models.generate_content(
        model=model_id,
        contents=f"You are a medical AI summarizer. I have a transcription of a video consultation, and I need a detailed and specific summary that focuses solely on the medical aspects discussed. The summary should not be generalized but instead should highlight key medical information, diagnoses, treatments, symptoms, and any relevant recommendations or instructions. Here's the transcription: {transcription}",
        config=GenerateContentConfig(
            tools=[google_search_tool],
            response_modalities=["TEXT"],
        )
    )

    # Extract the summary text from the response
    summary_text = ""
    for each in response.candidates[0].content.parts:
        summary_text += each.text
    
    return summary_text.strip()

@app.route('/summarize', methods=['POST'])
def summarize():
    # Define the JSON file path
    json_path = "data/transcriptions.json"

    # Load data from the JSON file
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Get the latest transcription (assuming the latest is the last entry)
    latest_transcription = data[-1]['Transcription']

    # Generate the summary for the latest transcription
    summary = generate_summary(latest_transcription)

    # Add the summary to the latest entry
    data[-1]['Summary'] = summary

    # Save the updated data back to the JSON file
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=4)

    print("Summarization complete for the latest transcription. The file has been updated.")
    return jsonify({"summary": summary})

if __name__ == "__main__":
    app.run(debug=True)
