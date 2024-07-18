from flask import Flask, render_template
import threading
import os
import game
import pygame

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def run_game():
    pygame.mixer.init()  # Initialize the Pygame mixer
    game.main()

if __name__ == "__main__":
    threading.Thread(target=run_game).start()
    port = int(os.environ.get("PORT", 5000))  # Use the port specified by Heroku
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=port)
