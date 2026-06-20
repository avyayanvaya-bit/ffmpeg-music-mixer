from flask import Flask, request, jsonify, send_file
import subprocess
import os
import random
import tempfile
import requests

app = Flask(__name__)

MUSIC_TRACKS = [
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
]

SEARCH_QUERIES = [
    "best life advice motivational speech",
    "entrepreneur success mindset talk",
    "billionaire advice young people",
    "great sportsman motivational speech",
    "business leader wisdom advice",
    "motivational interview success tips",
]

@app.route('/')
def health():
    return jsonify({"status": "running"})

@app.route('/get-video', methods=['GET'])
def get_video():
    tmpdir = tempfile.mkdtemp()
    video_path = os.path.join(tmpdir, 'video.%(ext)s')
    final_video = os.path.join(tmpdir, 'video.mp4')
    music_path = os.path.join(tmpdir, 'music.mp3')
    output_path = os.path.join(tmpdir, 'output.mp4')

    query = random.choice(SEARCH_QUERIES)

    try:
        # Download video using yt-dlp (simplified command)
        download_cmd = [
            'yt-dlp',
            f'ytsearch3:{query}',
            '--format', 'bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4][height<=720]/best',
            '--no-playlist',
            '-o', video_path,
            '--max-downloads', '1',
            '--no-warnings',
            '--merge-output-format', 'mp4',
        ]
        subprocess.run(download_cmd, timeout=120, check=True)

        # Find the downloaded file
        for f in os.listdir(tmpdir):
            if f.startswith('video') and f.endswith('.mp4'):
                final_video = os.path.join(tmpdir, f)
                break

        # Download random music
        music_url = random.choice(MUSIC_TRACKS)
        r = requests.get(music_url, timeout=30)
        with open(music_path, 'wb') as f:
            f.write(r.content)

        # Mix video with background music + crop to vertical
        subprocess.run([
            'ffmpeg', '-i', final_video,
            '-i', music_path,
            '-filter_complex',
            '[0:v]crop=ih*9/16:ih,scale=1080:1920[v];[1:a]volume=0.2[music];[0:a]volume=1.0[orig];[orig][music]amix=inputs=2:duration=first[a]',
            '-map', '[v]',
            '-map', '[a]',
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-t', '60',
            '-shortest',
            output_path
        ], timeout=180, check=True)

        return send_file(output_path, mimetype='video/mp4',
                        as_attachment=True,
                        download_name='video.mp4')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
