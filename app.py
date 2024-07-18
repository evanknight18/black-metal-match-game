from flask import Flask, render_template, request
import threading
import os
import pygame
from flask_socketio import SocketIO, emit
from PIL import Image
import io
import base64
import game
import signal

app = Flask(__name__)
socketio = SocketIO(app)
stop_event = threading.Event()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shutdown', methods=['POST'])
def shutdown():
    stop_event.set()
    func = request.environ.get('werkzeug.server.shutdown')
    if func:
        func()
    return 'Server shutting down...'

def run_game():
    pygame.init()
    pygame.mixer.init()
    screen_width, screen_height = 600, 700
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Black Metal Match-3 Game')

    game.init_game()  # Initialize the game

    def capture_frame(screen):
        image = pygame.image.tostring(screen, 'RGB')
        pil_image = Image.frombytes('RGB', screen.get_size(), image)
        buf = io.BytesIO()
        pil_image.save(buf, format='JPEG')
        frame = base64.b64encode(buf.getvalue()).decode('utf-8')
        return frame

    while not stop_event.is_set():
        if not game.main_loop(screen):
            break
        frame = capture_frame(screen)
        socketio.emit('frame', frame)
    pygame.quit()

if __name__ == "__main__":
    game_thread = threading.Thread(target=run_game)
    game_thread.start()
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, debug=True, use_reloader=False, host='0.0.0.0', port=port)
