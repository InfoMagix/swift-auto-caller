import subprocess

def play_mp3(file_path):
    subprocess.run(['mpg123', file_path])

from flask import Flask, request, render_template
import schedule
import time
import threading
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/schedule', methods=['POST'])
def schedule_play():
    play_time = request.form.get('play_time')
    file_path = request.form.get('file_path')
    schedule.every().day.at(play_time).do(play_mp3, file_path)
    return 'Scheduled to play {} at {}'.format(file_path, play_time)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    threading.Thread(target=run_schedule).start()
    app.run(host='0.0.0.0', port=5000)

