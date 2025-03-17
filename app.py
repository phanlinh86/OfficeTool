"""A Flask web application integrating LLM and Media functionalities.

This module creates a web interface for interacting with an AI assistant (via `llm.LLM`) and managing media files
(via `media.Media`). Users can chat with the AI, download media from URLs, play media files, record audio or video,
and capture screenshots. The application serves HTML templates and handles file uploads/downloads.

Key Features:
    - Chat interface with the AI assistant.
    - Media download from URLs with playback control.
    - Audio and video recording with configurable durations.
    - Screenshot capture with file download.
    - Simple web-based UI using Flask.

Dependencies:
    - flask: For creating the web server and handling routes.
    - llm: Custom module providing the `LLM` class for AI interactions.
    - media: Custom module providing the `Media` class for media operations.
    - os: For file and directory management.

Usage:
    Run the script directly (`python app.py`) to start the server, then access it at `http://127.0.0.1:5000/`.
"""


import lib.llm as llm
import lib.media as media
from flask import Flask, request, send_file, jsonify
import os
from time import time

app = Flask(__name__)

# Set upload/output directory
UPLOAD_FOLDER = media.out_path
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# HTML template for the frontend
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AI & Media Web App</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .section { margin-bottom: 20px; }
        textarea, input { width: 300px; }
        button { margin-top: 5px; }
        #chat-output { border: 1px solid #ccc; padding: 10px; height: 200px; overflow-y: auto; }
    </style>
</head>
<body>
    <h1>AI & Media Web App</h1>

    <div class="section">
        <h2>Chat with AI</h2>
        <textarea id="chat-input" placeholder="Type your message..."></textarea><br>
        <button onclick="sendChat()">Send</button>
        <div id="chat-output"></div>
    </div>

    <div class="section">
        <h2>Download Media</h2>
        <input type="text" id="media-url" placeholder="Enter URL (e.g., YouTube link)"><br>
        <button onclick="downloadMedia()">Download</button>
        <p id="download-output"></p>
    </div>

    <div class="section">
        <h2>Play Media</h2>
        <input type="text" id="play-file" placeholder="Enter file path"><br>
        <button onclick="playMedia()">Play</button>
        <button onclick="stopPlayback()">Stop</button>
        <p id="play-output"></p>
    </div>

    <div class="section">
        <h2>Record Audio/Video</h2>
        <input type="number" id="record-duration" placeholder="Duration (seconds)" min="1"><br>
        <button onclick="recordAudio()">Record Audio</button>
        <button onclick="recordVideo()">Record Video</button>
        <p id="record-output"></p>
    </div>

    <div class="section">
        <h2>Screenshot</h2>
        <button onclick="takeScreenshot()">Take Screenshot</button>
        <p id="screenshot-output"></p>
    </div>

    <script>
        async function fetchPost(url, data) {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            return response.json();
        }

        async function sendChat() {
            const input = document.getElementById('chat-input').value;
            const output = document.getElementById('chat-output');
            const result = await fetchPost('/chat', { message: input });
            output.innerHTML += `<p><b>You:</b> ${input}</p>`;
            if (result.response) {
                output.innerHTML += `<p><b>AI:</b> ${result.response}</p>`;
            } else {
                output.innerHTML += `<p><b>Error:</b> ${result.error}</p>`;
            }
            output.scrollTop = output.scrollHeight;
            document.getElementById('chat-input').value = '';
        }

        async function downloadMedia() {
            const url = document.getElementById('media-url').value;
            const output = document.getElementById('download-output');
            const result = await fetch('/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `url=${encodeURIComponent(url)}`
            }).then(res => res.json());
            output.innerHTML = result.file_path ? 
                `Downloaded: <a href="/download_file/${result.file_path.split('/').pop()}" download>${result.file_path}</a>` : 
                `Error: ${result.error}`;
        }

        async function playMedia() {
            const file = document.getElementById('play-file').value;
            const output = document.getElementById('play-output');
            const result = await fetch('/play', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `file_path=${encodeURIComponent(file)}`
            }).then(res => res.json());
            output.innerHTML = result.message || `Error: ${result.error}`;
        }

        async function stopPlayback() {
            const output = document.getElementById('play-output');
            const result = await fetch('/stop_playback', { method: 'POST' }).then(res => res.json());
            output.innerHTML = result.message || `Error: ${result.error}`;
        }

        async function recordAudio() {
            const duration = document.getElementById('record-duration').value;
            const output = document.getElementById('record-output');
            const result = await fetch('/record_audio', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `duration=${duration}`
            }).then(res => res.json());
            output.innerHTML = result.file_path ? 
                `Recorded: <a href="/download_file/${result.file_path.split('/').pop()}" download>${result.file_path}</a>` : 
                `Error: ${result.error}`;
        }

        async function recordVideo() {
            const duration = document.getElementById('record-duration').value;
            const output = document.getElementById('record-output');
            const result = await fetch('/record_video', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `duration=${duration}`
            }).then(res => res.json());
            output.innerHTML = result.file_path ? 
                `Recorded: <a href="/download_file/${result.file_path.split('/').pop()}" download>${result.file_path}</a>` : 
                `Error: ${result.error}`;
        }

        async function takeScreenshot() {
            const output = document.getElementById('screenshot-output');
            const result = await fetch('/screenshot', { method: 'POST' }).then(res => res.json());
            output.innerHTML = result.file_path ? 
                `Captured: <a href="/download_file/${result.file_path.split('/').pop()}" download>${result.file_path}</a>` : 
                `Error: ${result.error}`;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serves the main page of the web application."""
    return HTML_TEMPLATE  # Serve the embedded HTML directly

@app.route('/chat', methods=['POST'])
def chat():
    """Handles chat requests with the AI assistant.

    Expects a JSON payload with a 'message' field. Returns the AI's response.
    """
    data = request.get_json()
    message = data.get('message', '')
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    response = llm.chat(message)
    return jsonify({'response': response})

@app.route('/download', methods=['POST'])
def download():
    """Downloads media from a provided URL and returns the filepath."""
    url = request.form.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    file_path = media.download(url)
    if file_path:
        return jsonify({'file_path': file_path})
    return jsonify({'error': 'Download failed'}), 500

@app.route('/play', methods=['POST'])
def play():
    """Plays a media file specified by filepath."""
    file_path = request.form.get('file_path')
    if not file_path or not os.path.exists(file_path):
        return jsonify({'error': 'Invalid or missing file path'}), 400
    success = media.play(file_path)
    if success:
        return jsonify({'message': 'Playback started'})
    return jsonify({'error': 'Playback failed'}), 500

@app.route('/stop_playback', methods=['POST'])
def stop_playback():
    """Stops the currently playing media."""
    success = media.stop_playback()
    if success:
        return jsonify({'message': 'Playback stopped'})
    return jsonify({'error': 'No active playback'}), 400

@app.route('/record_audio', methods=['POST'])
def record_audio():
    """Records audio for a specified duration and returns the filepath."""
    duration = request.form.get('duration', type=int)
    if not duration or duration <= 0:
        return jsonify({'error': 'Invalid duration'}), 400
    filename = f"audio_{int(time.time())}.wav"
    success = media.record_audio(filename, duration)
    if success:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        return jsonify({'file_path': file_path})
    return jsonify({'error': 'Audio recording failed'}), 500

@app.route('/record_video', methods=['POST'])
def record_video():
    """Records video for a specified duration and returns the filepath."""
    duration = request.form.get('duration', type=int)
    if not duration or duration <= 0:
        return jsonify({'error': 'Invalid duration'}), 400
    filename = f"video_{int(time.time())}.avi"
    success = media.record_video(filename, duration)
    if success:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        return jsonify({'file_path': file_path})
    return jsonify({'error': 'Video recording failed'}), 500

@app.route('/screenshot', methods=['POST'])
def screenshot():
    """Captures a screenshot and returns the filepath."""
    filename = f"screenshot_{int(time.time())}.png"
    success = media.screenshot(filename)
    if success:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        return jsonify({'file_path': file_path})
    return jsonify({'error': 'Screenshot failed'}), 500

@app.route('/download_file/<path:filename>')
def download_file(filename):
    """Serves a file for download from the output directory."""
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)