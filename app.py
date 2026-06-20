from flask import Flask, request, jsonify, send_file
import subprocess
import requests
import os
import random
import tempfile

app = Flask(__name__)

MUSIC_TRACKS = [
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
]

@app.route('/mix', methods=['POST'])
def mix_audio():
    data = request.json
    video_url = data.get('video_url')
    
    tmpdir = tempfile.mkdtemp()
    video_path = os.path.join(tmpdir, 'video.mp4')
    music_path = os.path.join(tmpdir, 'music.mp3')
    output_path = os.path.join(tmpdir, 'output.mp4')
    
    r = requests.get(video_url)
    with open(video_path, 'wb') as f:
        f.write(r.content)
    
    music_url = random.choice(MUSIC_TRACKS)
    r = requests.get(music_url)
    with open(music_path, 'wb') as f:
        f.write(r.content)
    
    subprocess.run([
        'ffmpeg', '-i', video_path,
        '-i', music_path,
        '-filter_complex', '[1:a]volume=0.3[music];[0:a][music]amix=inputs=2:duration=first',
        '-c:v', 'copy',
        '-shortest',
        output_path
    ])
    
    return send_file(output_path, mimetype='video/mp4')

@app.route('/')
def health():
    return jsonify({"status": "running"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
