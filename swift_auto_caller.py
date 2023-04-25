# This script automatically plays audio files from a specified folder according to a defined schedule.
# It continuously loops through the folder and plays each file in alphanumeric order during the scheduled time periods.
# If no scheduled time period is active, the script waits for the next one.

import vlc
import os
import schedule
import time
import datetime
import threading
import argparse

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
folder_path = 'timmy_sounds'
playback_schedule = [
    ("07:00", "08:00"),
    ("18:00", "20:00"),
    ("21:00", "22:00"),
    ("22:17", "23:59")
]

# Sort the playback_schedule in ascending order
playback_schedule.sort()

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

def play_media_files_in_loop():
    while True:
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
                play_mp3(folder_path, media_file, start_time, end_time)
        else:
            next_start_time, next_end_time = playback_schedule[0]
            for start_time, end_time in playback_schedule:
                start_hour, start_minute = map(int, start_time.split(':'))
                scheduled_start_time = now.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)

                if now < scheduled_start_time:
                    next_start_time, next_end_time = start_time, end_time
                    break

            debug_print(f"Waiting for next play period: {next_start_time} - {next_end_time}")
            time.sleep(1)

# Run the script
play_media_files_in_loop()
