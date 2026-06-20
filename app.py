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

QUOTES = [
    "Success is not final, failure is not fatal.",
    "The harder you work, the luckier you get.",
    "Dream big. Start small. Act now.",
    "Your only limit is your mind.",
    "Push yourself because no one else will.",
    "Great things never come from comfort zones.",
    "It always seems impossible until it's done.",
    "Don't watch the clock. Do what it does. Keep going.",
    "Believe you can and you're halfway there.",
    "The secret of getting ahead is getting started.",
    "Success usually comes to those who are too busy to be looking for it.",
    "The way to get started is to quit talking and begin doing.",
]

PEXELS_QUERIES = [
    "motivation success",
    "nature inspiring",
    "city sunrise",
    "mountain adventure",
    "ocean waves calm",
    "fitness workout energy",
]

@app.route('/')
def health():
    return jsonify({"status": "running"})

@app.route('/get-video', methods=['POST'])
def get_video():
    data = request.json
    pexels_key = data.get('pexels_key')
    
    tmpdir = tempfile.mkdtemp()
    video_path = os.path.join(tmpdir, 'video.mp4')
    music_path = os.path.join(tmpdir, 'music.mp3')
    output_path = os.path.join(tmpdir, 'output.mp4')

    try:
        # Search Pexels for video
        query = random.choice(PEXELS_QUERIES)
        headers = {'Authorization': pexels_key}
        r = requests.get(
            'https://api.pexels.com/videos/search',
            headers=headers,
            params={'query': query, 'orientation': 'portrait', 'per_page': 10, 'size': 'medium'},
            timeout=30
        )
        videos = r.json()['videos']
        video = random.choice(videos)
        video_file = next((f for f in video['video_files'] if f['quality'] == 'sd' and f['file_type'] == 'video/mp4'), video['video_files'][0])
        
        # Download video
        vr = requests.get(video_file['link'], timeout=60)
        with open(video_path, 'wb') as f:
            f.write(vr.content)

        # Download music
        music_url = random.choice(MUSIC_TRACKS)
        mr = requests.get(music_url, timeout=30)
        with open(music_path, 'wb') as f:
            f.write(mr.content)

        # Pick random quote
        quote = random.choice(QUOTES)
        
        # Split quote into two lines if long
        words = quote.split()
        mid = len(words) // 2
        line1 = ' '.join(words[:mid])
        line2 = ' '.join(words[mid:])
        
        # FFmpeg: crop to vertical + add text + add music
        subprocess.run([
            'ffmpeg', '-i', video_path,
            '-i', music_path,
            '-filter_complex',
            f'[0:v]crop=ih*9/16:ih,scale=1080:1920[base];'
            f'[base]drawtext=text=\'{line1}\':fontcolor=white:fontsize=60:x=(w-text_w)/2:y=(h/2)-80:box=1:boxcolor=black@0.5:boxborderw=10,'
            f'drawtext=text=\'{line2}\':fontcolor=white:fontsize=60:x=(w-text_w)/2:y=(h/2)+20:box=1:boxcolor=black@0.5:boxborderw=10,'
            f'drawtext=text=\'Brilliant Minds\':fontcolor=gold:fontsize=45:x=(w-text_w)/2:y=100:box=1:boxcolor=black@0.6:boxborderw=8[v];'
            f'[1:a]volume=0.3[music];[0:a]volume=0.0[orig];[music]anull[a]',
            '-map', '[v]',
            '-map', '[a]',
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-t', '59',
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
