from flask import Flask, request, jsonify, send_file
import requests
import os
import random
import tempfile

app = Flask(__name__)

PEXELS_QUERIES = [
    "motivation success",
    "nature inspiring",
    "city sunrise",
    "mountain adventure",
    "fitness energy",
    "ocean calm",
]

@app.route('/')
def health():
    return jsonify({"status": "running"})

@app.route('/get-video', methods=['POST'])
def get_video():
    data = request.json
    pexels_key = data.get('pexels_key')

    tmpdir = tempfile.mkdtemp()
    output_path = os.path.join(tmpdir, 'video.mp4')

    try:
        query = random.choice(PEXELS_QUERIES)
        headers = {'Authorization': pexels_key}
        r = requests.get(
            'https://api.pexels.com/videos/search',
            headers=headers,
            params={
                'query': query,
                'orientation': 'portrait',
                'per_page': 15,
                'size': 'medium'
            },
            timeout=30
        )
        videos = r.json()['videos']
        video = random.choice(videos)
        
        # Get SD MP4 file
        video_file = next(
            (f for f in video['video_files'] 
             if f['quality'] == 'sd' and f['file_type'] == 'video/mp4'),
            video['video_files'][0]
        )

        # Download video
        vr = requests.get(video_file['link'], timeout=60)
        with open(output_path, 'wb') as f:
            f.write(vr.content)

        return send_file(
            output_path,
            mimetype='video/mp4',
            as_attachment=True,
            download_name='video.mp4'
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
