# This script automatically plays audio files from a specified folder according to a defined schedule.
# It continuously loops through the folder and plays each file in alphanumeric order during the scheduled time periods.
# If no scheduled time period is active, the script waits for the next one.


# - Python script implementation:
#     - Use the VLC library to play mp3 files.
#     - Use the `schedule` library for scheduling playback.
#     - Playback schedule: List of start and end times for daily play periods.
#     - Sort the playback schedule in ascending order.
#     - Loop through the mp3 file folder and play each mp3 file in alphanumeric order.
#     - Determine the current play period based on the system time.
#     - If the script starts outside a play period, print the next play period to the console.
#     - Schedule playback for each media file at the start time of each play period.
#     - Continuously loop through the folder and play the mp3 files during each play period.
#     - Provide debug information, such as scheduled events and playback times.


import vlc                     # needed for VLC media player functionality
import os                      # used for file manipulation and os-related functions
import schedule                # used for scheduling tasks
import time                    # used for sleep() function
import datetime                # used by get_current_schedule(), get_next_schedule()
import threading               # used for running tasks in parallel
import argparse                # used for handling command-line arguments

from flask import Flask, request, redirect, url_for, jsonify, render_template, flash, send_from_directory
from mutagen.mp3 import MP3    # used for handling MP3 metadata
from datetime import timedelta # used for datetime calculations

# needed for the file upload facility
from werkzeug.utils import secure_filename

import shutil                  # used by delete_file()


# controsl while file types are alloed to be uploaded
ALLOWED_EXTENSIONS = {'mp3'}

# to hold the name of the mp3 that is currently playing
currently_playing = ""

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- scheduling functions...

def get_current_schedule():
    now_dt = datetime.datetime.now()
    now = now_dt.time()
    for start_time, end_time in playback_schedule:
        start_hour, start_minute = map(int, start_time.split(':'))
        end_hour, end_minute = map(int, end_time.split(':'))
        start_time_dt = now_dt.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0).timetz()
        end_time_dt = now_dt.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0).timetz()
        if start_time_dt <= now <= end_time_dt:
            return {"start_time": start_time, "end_time": end_time}
    return {"start_time": "N/A", "end_time": "N/A"}


def get_next_schedule():
    now_dt = datetime.datetime.now()
    now = now_dt.time()
    next_start_time = None
    next_end_time = None
    min_time_diff = float('inf')
    next_schedule_tomorrow = False

    for start_time, end_time in playback_schedule:
        start_hour, start_minute = map(int, start_time.split(':'))
        scheduled_start_time = now_dt.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0).time()

        if scheduled_start_time > now:
            time_diff = (datetime.datetime.combine(datetime.date.today(), scheduled_start_time) - datetime.datetime.combine(datetime.date.today(), now)).seconds
            if time_diff < min_time_diff:
                min_time_diff = time_diff
                next_start_time = start_time
                next_end_time = end_time
                next_schedule_tomorrow = False

    if next_start_time is None:  # No next schedule today, check for tomorrow
        min_time_diff = float('inf')
        for start_time, end_time in playback_schedule:
            start_hour, start_minute = map(int, start_time.split(':'))
            scheduled_start_time = now_dt.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0) + datetime.timedelta(days=1)
            time_diff = (scheduled_start_time - now_dt).seconds
            if time_diff < min_time_diff:
                min_time_diff = time_diff
                next_start_time = start_time
                next_end_time = end_time
                next_schedule_tomorrow = True

    if next_start_time and next_end_time:
        return {"start_time": next_start_time, "end_time": next_end_time, "tomorrow": next_schedule_tomorrow}
    return {"start_time": "N/A", "end_time": "N/A", "tomorrow": False}


def get_currently_playing_mp3():
    # Replace the logic to get the currently playing MP3 file based on your application
    return currently_playing


# -----------------------


# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--debug', action='store_true', help='Enable debug mode')
args = parser.parse_args()

# Debug switch
debug = args.debug

def debug_print(*args, **kwargs):
    if debug:
        print(*args, **kwargs)

# Print system time as a debug measure
debug_print(f"Swift Caller auto player")
debug_print("===========================\n")

debug_print(f"Current time is {time.strftime('%H:%M:%S')}\n")

# Define variables
folder_path = 'bird_calls'
#folder_path = 'timmy_sounds'

# this is the default schedule
playback_schedule = [
    ("07:00", "08:00"),
    ("17:00", "18:00"),
    ("23:40", "23:45"), 
    ("23:55", "23:59"),        
]

# Load the schedule from the file if it exists.  this is made when the user edits the schedule on index.html
if os.path.exists('playback_schedule.txt'):
    with open('playback_schedule.txt', 'r') as f:
        lines = f.readlines()
        playback_schedule = [tuple(line.strip().split(',')) for line in lines]


# Sort the playback_schedule in ascending order
playback_schedule.sort()

# Add this line after the playback_schedule variable
stop_flag = False


# Playback schedule for debug purposes
for i, (start_time, end_time) in enumerate(playback_schedule):
    debug_print(f"Time slot {i+1}: {start_time} - {end_time}")
debug_print("")

# Print list of files
media_files = [f for f in os.listdir(folder_path) if f.endswith('.mp3')]
media_files.sort()  # Sort the media files in alphanumeric order

debug_print(f"Files in {folder_path}:")
for f in media_files:
    debug_print(f)


# Define functions
def play_mp3(folder_path, media_file, start_time, end_time):
    global player
    instance = vlc.Instance('--aout=alsa')
    player = instance.media_player_new()
    media = instance.media_new(os.path.join(folder_path, media_file))
    player.set_media(media)
    player.play()
    current_time = time.strftime('%H:%M:%S')
    debug_print(f"Now playing at {current_time}: {media_file}")
    while True:
        state = player.get_state()
        if state == vlc.State.Ended:
            break
    player.stop()
    instance.release()

def update_volume(volume):
    global player
    if player:
        player.audio_set_volume(volume)

def save_volume_to_file(volume):
    with open('volume.txt', 'w') as f:
        f.write(str(volume))


def load_volume_from_file():
    if os.path.exists('volume.txt'):
        with open('volume.txt', 'r') as f:
            volume = int(f.read().strip())
    else:
        volume = 50  # default volume if no file exists
    return volume


# Add a global variable for the VLC player after the stop_flag variable
player = None
initial_volume = load_volume_from_file()
update_volume(initial_volume)





def play_media_files_in_loop():
    global currently_playing
    while not stop_flag:
        now = datetime.datetime.now()
        play_period = None

        for start_time, end_time in playback_schedule:
            start_hour, start_minute = map(int, start_time.split(':'))
            end_hour, end_minute = map(int, end_time.split(':'))
            scheduled_start_time = now.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
            scheduled_end_time = now.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)

            if scheduled_end_time <= scheduled_start_time:
                scheduled_end_time += datetime.timedelta(days=1)

            if scheduled_start_time <= now < scheduled_end_time:
                play_period = (scheduled_start_time, scheduled_end_time)
                debug_print(f"\nPlaying between {start_time} and {end_time}")
                break

        if play_period is not None:
            for media_file in media_files:
                currently_playing = media_file
                play_mp3(folder_path, media_file, start_time, end_time)
            currently_playing = ""
        else:
            next_start_time, next_end_time = playback_schedule[0]
            for start_time, end_time in playback_schedule:
                start_hour, start_minute = map(int, start_time.split(':'))
                scheduled_start_time = now.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)

                if now < scheduled_start_time:
                    next_start_time, next_end_time = start_time, end_time
                    break

            if now > scheduled_start_time:
                scheduled_start_time += datetime.timedelta(days=1)

            debug_print(f"Waiting for next play period: {next_start_time} - {next_end_time}")
            time_to_next_period = (scheduled_start_time - now).total_seconds()
            time.sleep(min(1, time_to_next_period))

def start_playback():
    global stop_flag
    stop_flag = False
    play_media_files_in_loop()

def stop_playback():
    global stop_flag
    stop_flag = True

# get mp3 file durations of ALL mp3 files
def get_durations(mp3_files):
    durations = []
    for mp3_file in mp3_files:
        audio = MP3(os.path.join(app.config['UPLOAD_FOLDER'], mp3_file))
        duration = timedelta(seconds=int(audio.info.length))
        durations.append(str(duration))
    return durations

# get duration of a single mp3 file
def get_duration_singlefile(file_path):
    audio = MP3(file_path)
    duration = timedelta(seconds=int(audio.info.length))
    return str(duration)


def get_sorted_mp3_files():
    mp3_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.lower().endswith('.mp3')]
    mp3_files.sort()
    return mp3_files




# Flask app and routes
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = folder_path
# Flask requires a secret_key to be set for the application to use session-based features, like flashing messages.
app.secret_key = 'your_secret_key_here'

# Update the index route to pass the current_schedule, next_schedule, and currently_playing to the template
@app.route('/')
def index():
    current_schedule = get_current_schedule()
    next_schedule = get_next_schedule()
    currently_playing = get_currently_playing_mp3()
    return render_template('index.html', playback_schedule=playback_schedule, current_schedule=current_schedule, next_schedule=next_schedule, currently_playing=currently_playing)


@app.route('/update_schedule', methods=['POST'])
def update_schedule():
    global playback_schedule
    new_schedule = []

    for i in range(len(playback_schedule)):
        start_time = request.form.get(f'start_time_{i}')
        end_time = request.form.get(f'end_time_{i}')
        if start_time and end_time:
            new_schedule.append((start_time, end_time))

    playback_schedule = new_schedule
    playback_schedule.sort()

    # Save the updated schedule to a file
    with open('playback_schedule.txt', 'w') as f:
        for start_time, end_time in playback_schedule:
            f.write(f"{start_time},{end_time}\n")

    return redirect(url_for('index'))


@app.route('/start_playback', methods=['POST'])
def start_playback_route():
    global playback_thread
    if playback_thread is None or not playback_thread.is_alive():
        playback_thread = threading.Thread(target=start_playback)
        playback_thread.start()
    return redirect(url_for('index'))

@app.route('/stop_playback', methods=['POST'])
def stop_playback_route():
    stop_playback()
    return redirect(url_for('index'))

@app.route('/add_row', methods=['POST'])
def add_row():
    global playback_schedule
    now = datetime.datetime.now()
    default_start_time = (now + timedelta(hours=1)).strftime('%H:%M')
    default_end_time = (now + timedelta(hours=2)).strftime('%H:%M')
    playback_schedule.append((default_start_time, default_end_time))
    playback_schedule.sort()
    return redirect(url_for('index'))


@app.route('/delete_row/<int:row_index>', methods=['POST'])
def delete_row(row_index):
    global playback_schedule
    if 0 <= row_index < len(playback_schedule):
        del playback_schedule[row_index]
    return redirect(url_for('index'))

@app.route('/get_currently_playing', methods=['GET'])
def get_currently_playing():
    currently_playing = get_currently_playing_mp3()
    if currently_playing:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], currently_playing)
        duration = get_duration_singlefile(file_path)
        return jsonify(currently_playing=currently_playing, duration=duration)
    else:
        return jsonify(currently_playing="Nothing is playing right now.")

@app.route('/set_volume', methods=['POST'])
def set_volume():
    volume = request.json.get('volume', 50)
    update_volume(int(volume))
    save_volume_to_file(volume)
    return jsonify({"success": True})

@app.route('/get_saved_volume', methods=['GET'])
def get_saved_volume():
    volume = load_volume_from_file()
    return jsonify({'volume': volume})



# upload page routes..

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File uploaded successfully')
            return redirect(url_for('upload_file'))
    
    mp3_files = get_sorted_mp3_files()
    durations = get_durations(mp3_files)
    mp3_files_with_durations = zip(mp3_files, durations)
    return render_template('upload.html', mp3_files_with_durations=mp3_files_with_durations)



@app.route('/delete_file/<path:filename>', methods=['POST'])
def delete_file(filename):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.remove(file_path)
        flash('File deleted successfully')
    except Exception as e:
        flash('Error deleting file: {}'.format(e))

    return redirect(url_for('upload_file'))


# Add this route to render the upload page
@app.route('/upload')
def upload():
    mp3_files = get_all_mp3_files()
    sorted_mp3_files = sorted(mp3_files)
    return render_template('upload.html', mp3_files=sorted_mp3_files)

@app.route('/uploaded_file/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)



# Run the script in separate threads
if __name__ == "__main__":
    web_server = threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5000})
    web_server.start()

    playback_thread = threading.Thread(target=play_media_files_in_loop)
    playback_thread.start()





