# This script automatically plays audio files from a specified folder according to a defined schedule.
# It continuously loops through the folder and plays each file in alphanumeric order during the scheduled time periods.
# If no scheduled time period is active, the script waits for the next one.

import vlc
import os
import schedule
import time
import datetime
import threading

# Print system time as a debug measure
print(f"Swift Caller auto player")
print("===========================\n")

print(f"Current time is {time.strftime('%H:%M:%S')}\n")
#print("")

# Define variables
folder_path = 'timmy_sounds'
playback_schedule = [
    ("16:13", "16:15"),
    ("16:16", "16:17"),
    ("16:20", "17:30"),
    ("18:00", "20:30"),
    ("22:17", "23:00")
]

# Sort the playback_schedule in ascending order
playback_schedule.sort()

# Playback schedule for debug purposes
for i, (start_time, end_time) in enumerate(playback_schedule):
    print(f"Time slot {i+1}: {start_time} - {end_time}")
print("")

# Print list of files
media_files = [f for f in os.listdir(folder_path) if f.endswith('.mp3')]
media_files.sort()  # Add this line to sort the media files in alphanumeric order

print(f"Files in {folder_path}:")
for f in media_files:
    print(f)


# Define functions
def play_mp3(folder_path, media_file, start_time, end_time):
    instance = vlc.Instance('--aout=alsa')
    player = instance.media_player_new()
    media = instance.media_new(os.path.join(folder_path, media_file))
    player.set_media(media)
    player.play()
    current_time = time.strftime('%H:%M:%S')
    print(f"Now playing at {current_time}: {media_file}")
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
                print(f"\nPlaying between {start_time} and {end_time}")
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

            print(f"Waiting for next play period: {next_start_time} - {next_end_time}")
            time.sleep(1)

# Run the script
play_media_files_in_loop()
