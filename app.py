from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret')
sio = SocketIO(app, async_mode='threading', cors_allowed_origins='*')

# --- Simple in-memory game state (one game at a time) ---
state = {
    'picker_sid': None,    # client1
    'guesser_sid': None,   # client2
    'secret': None,
    'attempts': 0,
    'running': False,
}

# --- HTTP routes (interfaces) ---
@app.get('/')
def index():
    return render_template('index.html')

@app.get('/picker')
def picker():
    return render_template('picker.html')

@app.get('/guesser')
def guesser():
    return render_template('guesser.html')

# --- Socket.IO events ---
@sio.on('connect')
def on_connect():
    emit('server_info', {'running': state['running']})

@sio.on('register_picker')
def register_picker():
    state['picker_sid'] = request.sid
    emit('picker_registered', {'ok': True})

@sio.on('register_guesser')
def register_guesser():
    state['guesser_sid'] = request.sid
    emit('guesser_registered', {'ok': True})
    # If the game is already ready, inform guesser
    if state['running'] and state['secret'] is not None:
        sio.emit('start_guessing')

@sio.on('set_secret')
def set_secret(data):
    if request.sid != state['picker_sid']:
        emit('error_msg', {'error': "Seul le Client1 (choisisseur) peut définir le nombre."})
        return
    try:
        n = int(data.get('number'))
    except (TypeError, ValueError):
        emit('error_msg', {'error': 'Veuillez entrer un entier.'})
        return
    if n < 0 or n > 100:
        emit('error_msg', {'error': 'Le nombre doit être entre 0 et 100.'})
        return
    state['secret'] = n
    state['attempts'] = 0
    state['running'] = True
    emit('secret_ok', {'ok': True})
    # Notify guesser to start
    if state['guesser_sid']:
        sio.emit('start_guessing', room=state['guesser_sid'])

@sio.on('guess')
def on_guess(data):
    if not state['running']:
        emit('error_msg', {'error': "Aucune partie en cours."})
        return
    if request.sid != state['guesser_sid']:
        emit('error_msg', {'error': "Seul le Client2 (devin) peut proposer un essai."})
        return
    try:
        g = int(data.get('number'))
    except (TypeError, ValueError):
        emit('feedback', {'result': 'ERROR', 'message': 'Entrez un entier 0–100.'})
        return
    if g < 0 or g > 100:
        emit('feedback', {'result': 'ERROR', 'message': 'Entrez un entier 0–100.'})
        return

    state['attempts'] += 1
    secret = state['secret']
    if g > secret:
        emit('feedback', {'result': 'HIGH'})
    elif g < secret:
        emit('feedback', {'result': 'LOW'})
    else:
        emit('feedback', {'result': 'BRAVO', 'attempts': state['attempts']})
        # Inform picker as well
        if state['picker_sid']:
            sio.emit('game_over', {'attempts': state['attempts'], 'secret': secret}, room=state['picker_sid'])
        # Reset game
        state['running'] = False
        state['secret'] = None
        state['attempts'] = 0

@sio.on('restart')
def on_restart():
    # Allow picker to restart a new game quickly
    if request.sid == state['picker_sid']:
        state['secret'] = None
        state['attempts'] = 0
        state['running'] = False
        emit('restarted', {'ok': True})

# --- Entrypoint ---
if __name__ == '__main__':
    # Bind on all interfaces so other PCs can connect (replace host with server IP when launching)
    port = int(os.environ.get('PORT', 5000))
    sio.run(app, host='0.0.0.0', port=port)
