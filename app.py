from flask import Flask, render_template
import threading
import os
import pygame
from flask_socketio import SocketIO, emit
from PIL import Image
import io
import base64
import game

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

def run_game():
    pygame.init()
    pygame.mixer.init()
    screen_width, screen_height = 600, 700
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Black Metal Match-3 Game')

    def capture_frame(screen):
        image = pygame.image.tostring(screen, 'RGB')
        pil_image = Image.frombytes('RGB', screen.get_size(), image)
        buf = io.BytesIO()
        pil_image.save(buf, format='JPEG')
        frame = base64.b64encode(buf.getvalue()).decode('utf-8')
        return frame

    while True:
        game.main_loop(screen)  # Ensure game.main_loop() handles one iteration of the game loop
        frame = capture_frame(screen)
        socketio.emit('frame', frame)

if __name__ == "__main__":
    threading.Thread(target=run_game).start()
    port = int(os.environ.get("PORT", 5000))  # Use the port specified by Heroku
    socketio.run(app, debug=True, host='0.0.0.0', port=port)
