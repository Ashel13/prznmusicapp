from flask import Flask, render_template, request, session, redirect, url_for
import os

app = Flask(__name__)
# Security key
app.secret_key = os.environ.get('SECRET_KEY', 'super_secret_key_123')

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
