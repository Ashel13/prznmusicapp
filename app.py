import requests
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'change_this_to_random_secret_key'

# --- CONFIGURATION ---
# We use a public Piped instance. If this one is slow, find others online.
PIPED_API_URL = "https://pipedapi.kavin.rocks"

USERS = {
    "prazoon": "king123",
    "brother": "bro2026"
}

# --- ROUTES ---
@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('player'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username').lower()
    password = request.form.get('password')
    if username in USERS and USERS[username] == password:
        session['user'] = username
        return redirect(url_for('player'))
    return "Wrong password! <a href='/'>Try Again</a>"

@app.route('/player')
def player():
    if 'user' not in session: return redirect(url_for('index'))
    return render_template('player.html', user=session['user'])

@app.route('/search')
def search():
    if 'user' not in session: return jsonify([])
    query = request.args.get('q')
    
    # Use Piped API to search
    try:
        response = requests.get(f"{PIPED_API_URL}/search?q={query}&filter=music_songs")
        data = response.json()
        # Clean up the data for our frontend
        results = []
        for item in data.get('items', [])[:10]: # Get top 10 results
            results.append({
                'title': item['title'],
                'artist': item.get('uploaderName', 'Unknown'),
                'thumbnail': item['thumbnail'],
                'videoId': item['url'].split('=')[-1] # Extract ID
            })
        return jsonify(results)
    except Exception as e:
        print(e)
        return jsonify([])

@app.route('/get_stream')
def get_stream():
    if 'user' not in session: return "Unauthorized", 401
    video_id = request.args.get('id')
    
    # Get the direct audio link from Piped
    try:
        response = requests.get(f"{PIPED_API_URL}/streams/{video_id}")
        data = response.json()
        
        # Find the best audio-only stream
        for stream in data['audioStreams']:
            if stream['format'] == 'M4A':
                return redirect(stream['url'])
                
        return "No audio found", 404
    except:
        return "Error fetching stream", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)