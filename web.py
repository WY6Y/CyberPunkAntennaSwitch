# WY6YPi Antenna Switch
# Copyright (c) 2025 Stephen Houser WY6Y
# Licensed under CC BY-NC 4.0 (https://creativecommons.org/licenses/by-nc/4.0/)
from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session
from flask_session import Session
import subprocess
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'USER' and password == 'MAKEAPASSWORD':
            session['logged_in'] = True
            return redirect(url_for('index'))
        return '<h2 style="color:#ff00ff">Access Denied</h2>', 401
    return '''
    <h2 style="color:#00ffff">Cyber Access</h2>
    <form method="post" style="color:#0f0">
        <input type="text" name="username" placeholder="Username" style="background:#1a1a1a;color:#0f0;border:1px solid #00ffff"><br>
        <input type="password" name="password" placeholder="Password" style="background:#1a1a1a;color:#0f0;border:1px solid #00ffff"><br>
        <input type="submit" value="Enter" style="background:#ff00ff;color:#000;padding:10px;">
    </form>
    '''

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>WY6YPi Antenna Switch</title>
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {
                background-image: url('/static/cyberpunk-bg.jpg');
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
                color: #0f0;
                font-family: 'Orbitron', sans-serif;
                text-align: center;
                padding: 50px;
                position: relative;
                overflow: hidden;
            }
            body::after {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: repeating-linear-gradient(
                    0deg,
                    rgba(0, 0, 0, 0.1),
                    rgba(0, 0, 0, 0.1) 2px,
                    transparent 2px,
                    transparent 4px
                );
                animation: scanline 10s linear infinite;
                pointer-events: none;
            }
            h1 {
                font-size: 3em;
                text-shadow: 0 0 15px #0f0, 0 0 30px #0f0;
                animation: glitch 2s linear infinite;
            }
            #state {
                font-size: 1.8em;
                margin: 30px 0;
                text-shadow: 0 0 10px #0f0;
                animation: pulse 2s infinite;
            }
            .button {
                background-color: #111;
                border: 2px solid #0f0;
                color: #0f0;
                padding: 15px 30px;
                margin: 15px;
                font-size: 1.4em;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 0 10px #0f0, 0 0 20px #0f0;
                animation: buttonPulse 1.5s infinite;
            }
            .button:hover {
                background-color: #0f0;
                color: #000;
                box-shadow: 0 0 30px #0f0, 0 0 60px #0f0;
            }
            .button:active {
                transform: scale(0.95);
            }
            @keyframes glitch {
                0% { transform: translate(0); }
                20% { transform: translate(-2px, 2px); }
                40% { transform: translate(-2px, -2px); }
                60% { transform: translate(2px, 2px); }
                80% { transform: translate(2px, -2px); }
                100% { transform: translate(0); }
            }
            @keyframes pulse {
                0% { text-shadow: 0 0 5px #0f0; }
                50% { text-shadow: 0 0 20px #0f0; }
                100% { text-shadow: 0 0 5px #0f0; }
            }
            @keyframes buttonPulse {
                0% { box-shadow: 0 0 10px #0f0, 0 0 20px #0f0; }
                50% { box-shadow: 0 0 15px #0f0, 0 0 30px #0f0; }
                100% { box-shadow: 0 0 10px #0f0, 0 0 20px #0f0; }
            }
            @keyframes scanline {
                0% { transform: translateY(-100%); }
                100% { transform: translateY(100%); }
            }
        </style>
    </head>
    <body>
        <h1>WY6YPi Antenna Switch</h1>
        <div id="state">Current Antenna: Loading...</div>
        <button class="button" onclick="switchAntenna('0')">STORM MODE</button>
        <button class="button" onclick="switchAntenna('1')">Antenna 1 (Doublet)</button>
        <button class="button" onclick="switchAntenna('2')">Antenna 2 (Emcomm III-B)</button>
        <button class="button" onclick="switchAntenna('3')">Antenna 3 (Aux)</button>
        <script>
            function updateState() {
                fetch('/state')
                    .then(response => response.json())
                    .then(data => {
                        let stateText = data.state === '0' ? 'All antennas grounded' : `Antenna ${data.state} (${data.label})`;
                        document.getElementById('state').innerText = `Current Antenna: ${stateText}`;
                    })
                    .catch(error => console.error('State error:', error));
            }
            function switchAntenna(antenna) {
                document.getElementById('state').innerText = 'Switching...';
                fetch('/switch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: `antenna=${antenna}`
                })
                .then(response => response.json())
                .then(data => {
                    if (data.message) {
                        document.getElementById('state').innerText = 'Error: ' + data.message;
                    } else {
                        updateState();
                    }
                })
                .catch(error => {
                    console.error('Switch error:', error);
                    document.getElementById('state').innerText = 'Switch failed';
                });
            }
            updateState();
        </script>
    </body>
    </html>
    ''')

@app.route('/state')
def get_state():
    state_file = '/home/user/antenna_switch/state.txt'
    try:
        with open(state_file, 'r') as f:
            state = f.read().strip()
    except FileNotFoundError:
        state = '0'
        with open(state_file, 'w') as f:
            f.write(state)
        os.chmod(state_file, 0o666)  # Ensure all users can read/write
    labels = {'0': 'All Grounded', '1': 'Doublet', '2': 'Emcomm III-B', '3': 'Aux'}
    return jsonify({'state': state, 'label': labels.get(state, 'Unknown')})

@app.route('/switch', methods=['POST'])
def switch():
    antenna = request.form.get('antenna')
    print(f"Switching to {antenna}")
    state_file = '/home/user/antenna_switch/state.txt'
    try:
        result = subprocess.run(['sudo', './switch_antenna.py', antenna], check=True, capture_output=True, text=True)
        print(f"Output: {result.stdout}")
        print(f"Error (if any): {result.stderr}")
        with open(state_file, 'w') as f:
            f.write(antenna)
        os.chmod(state_file, 0o666)  # Ensure all users can read/write
        labels = {'0': 'All Grounded', '1': 'Doublet', '2': 'Emcomm III-B', '3': 'Aux'}
        return jsonify({'state': antenna, 'label': labels.get(antenna, 'Unknown')})
    except subprocess.CalledProcessError as e:
        print(f"Subprocess error: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return jsonify({'message': f'Subprocess error: {e.stderr}'}), 500
    except Exception as e:
        print(f"General error: {e}")
        return jsonify({'message': f'General error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
