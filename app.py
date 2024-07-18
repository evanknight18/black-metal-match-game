from flask import Flask, render_template
import threading
import game

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def run_game():
    game.main()

if __name__ == "__main__":
    threading.Thread(target=run_game).start()
    app.run(debug=True, use_reloader=False, host='0.0.0.0')
