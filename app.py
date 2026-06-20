from flask import Flask, request, jsonify, send_file
import subprocess
import os
import random
import tempfile
import json

app = Flask(__name__)

MUSIC_TRACKS = [
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
]

SEARCH_QUERIES = [
    "best life advice motivational speech",
    "CEO entrepreneur success mindset talk",
    "billionaire advice young people motivational",
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
    video_path = os.path.join(tmpdir, 'video.mp4')
    music_path = os.path.join(tmpdir, 'music.mp3')
    output_path = os.path.join(tmpdir, 'output.mp4')

    # Pick random search query
    query = random.choice(SEARCH_QUERIES)

    # Search YouTube for Creative Commons videos and download a clip
    search_cmd = [
        'yt-dlp',
        f'ytsearch5:{query}',
        '--match-filter', 'license=creativecommon',
        '--get-url',
        '--format', 'mp4/best[height<=720]',
        '--no-playlist',
        '-o', video_path,
        '--download-sections', '*30-90',
        '--force-keyframes-at-cuts',
    ]

    try:
        # Download video using yt-dlp
        download_cmd = [
            'yt-dlp',
            f'ytsearch5:{query}',
            '--match-filter', 'license=creativecommon',
            '--format', 'mp4/best[height<=720]',
            '--no-playlist',
            '-o', video_path,
            '--download-sections', '*30-90',
            '--force-keyframes-at-cuts',
            '--max-downloads', '1',
        ]
        subprocess.run(download_cmd, timeout=120, check=True)

        # Download random music
        import requests as req
        music_url = random.choice(MUSIC_TRACKS)
        r = req.get(music_url, timeout=30)
        with open(music_path, 'wb') as f:
            f.write(r.content)

        # Mix video with background music using FFmpeg
        # Crop to vertical 9:16 format
        subprocess.run([
            'ffmpeg', '-i', video_path,
            '-i', music_path,
            '-filter_complex',
            '[0:v]crop=ih*9/16:ih,scale=1080:1920[v];[1:a]volume=0.2[music];[0:a][music]amix=inputs=2:duration=first[a]',
            '-map', '[v]',
            '-map', '[a]',
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-shortest',
            output_path
        ], timeout=180, check=True)

        return send_file(output_path, mimetype='video/mp4')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
