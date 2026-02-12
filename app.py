import requests
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'super_secret_key_123')

# --- CONFIGURATION ---
# Current working API
PIPED_API_URL = "https://pipedapi.kavin.rocks"

USERS = {
    "prazoon": "king123",
    "brother": "bro2026"
}

@app.route('/')
def index():
    if 'user' in session: return redirect(url_for('player'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username').lower()
    password = request.form.get('password')
    if username in USERS and USERS[username] == password:
        session['user'] = username
        return redirect(url_for('player'))
    return "Wrong password! <a href='/'>Try Again</a>"

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/player')
def player():
    if 'user' not in session: return redirect(url_for('index'))
    return render_template('player.html', user=session['user'])

@app.route('/search')
def search():
    if 'user' not in session: return jsonify([])
    query = request.args.get('q')
    
    try:
        response = requests.get(f"{PIPED_API_URL}/search?q={query}&filter=music_songs", timeout=10)
        data = response.json()
        
        results = []
        for item in data.get('items', [])[:15]: 
            if 'url' in item:
                results.append({
                    'title': item['title'],
                    'artist': item.get('uploaderName', 'Unknown'),
                    'thumbnail': item['thumbnail'],
                    'videoId': item['url'].split('=')[-1]
                })
        return jsonify(results)
    except Exception as e:
        print(f"SEARCH ERROR: {e}")
        return jsonify([])

@app.route('/get_stream')
def get_stream():
    if 'user' not in session: return "Unauthorized", 401
    video_id = request.args.get('id')
    
    try:
        response = requests.get(f"{PIPED_API_URL}/streams/{video_id}", timeout=10)
        data = response.json()
        
        # Try to find M4A first
        for stream in data['audioStreams']:
            if stream['format'] == 'M4A':
                return redirect(stream['url'])
                
        # Fallback to any audio
        if data['audioStreams']:
            return redirect(data['audioStreams'][0]['url'])
            
        return "No audio found", 404
    except:
        return "Error fetching stream", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

