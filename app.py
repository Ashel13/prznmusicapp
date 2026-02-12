import requests
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'super_secret_key_123')

# --- CONFIGURATION: THE MULTI-ENGINE LIST ---
# The app will try these one-by-one until it finds a working server.
PIPED_SERVERS = [
    "https://pipedapi.kavin.rocks",
    "https://api.piped.privacy.com.de",
    "https://pipedapi.drgns.space",
    "https://pipedapi.tokhmi.xyz",
    "https://pipedapi.smnz.de",
    "https://api.piped.projectsegfau.lt",
    "https://pipedapi.moomoo.me"
]

USERS = {
    "prazoon": "king123",
    "brother": "bro2026"
}

# --- HELPER: FIND WORKING SERVER ---
def fetch_from_piped(endpoint):
    """Tries all servers in the list until one works"""
    for server in PIPED_SERVERS:
        try:
            url = f"{server}{endpoint}"
            print(f"Trying engine: {server}...") # Debug log
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            continue # If this server fails, try the next one
    return None # All servers failed

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
    
    # Use the helper to try ALL servers
    data = fetch_from_piped(f"/search?q={query}&filter=music_songs")
    
    if not data:
        print("ALL ENGINES FAILED")
        return jsonify([])

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

@app.route('/get_stream')
def get_stream():
    if 'user' not in session: return "Unauthorized", 401
    video_id = request.args.get('id')
    
    # Use the helper to try ALL servers
    data = fetch_from_piped(f"/streams/{video_id}")
    
    if not data:
        return "Error: All servers are busy.", 500

    try:
        # Try to find M4A first
        for stream in data['audioStreams']:
            if stream['format'] == 'M4A':
                return redirect(stream['url'])
        
        # Fallback to any audio
        if data['audioStreams']:
            return redirect(data['audioStreams'][0]['url'])
            
        return "No audio found", 404
    except:
        return "Stream Error", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
