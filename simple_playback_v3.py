# simplest working version that loops through a folder and plays each file once
# adds a schedule.  Schedule does not work quite right though and only playes files once per play_period
# now loops through the folder for each time period.  not convinced schedule is correct


import vlc
import os
import schedule
import time
import datetime
import threading

# print system time as a debug measure
print(f"Current time: {time.strftime('%H:%M:%S')}")

# Define variables
folder_path = 'timmy_sounds'
# playback_schedule = [
#     ("00:00", "01:00"),
#     ("06:00", "09:00"),
#     ("12:00", "17:00"),
#     ("18:00", "21:00")
# ]

playback_schedule = [
    ("16:13", "16:15"),
    ("16:16", "16:17"),
    ("16:20", "17:30"),
    ("19:00", "20:30"),
    ("22:17", "23:00")
]


# Sort the playback_schedule in ascending order
playback_schedule.sort()

# playback schedule for debug purposes
for i, (start_time, end_time) in enumerate(playback_schedule):
    print(f"Time slot {i+1}: {start_time} - {end_time}")
print("")

# Print list of files
media_files = [f for f in os.listdir(folder_path) if f.endswith('.mp3')]
print(f"Files in {folder_path}:")
for f in media_files:
    print(f)

# Define functions
def play_mp3(folder_path, media_file, start_time, end_time):
    print(f"\nPlaying between {start_time} and {end_time}")
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
                break

        if play_period is not None:
            for media_file in media_files:
                play_mp3(folder_path, media_file)
        else:
            time.sleep(1)

def print_first_50_scheduled_events():
    print("\nFirst 50 scheduled events:")
    for i, job in enumerate(schedule.jobs[:50]):
        print(f"{i + 1}. Job '{job.job_func.__name__}' scheduled at {job.next_run.strftime('%Y-%m-%d %H:%M:%S')}")

def schedule_playback():
    # Sort the media files in alphanumeric order
    media_files.sort()

    for start_time, end_time in playback_schedule:
        start_hour, start_minute = map(int, start_time.split(':'))
        end_hour, end_minute = map(int, end_time.split(':'))

        for media_file in media_files:
            schedule.every().day.at(f"{start_hour:02d}:{start_minute:02d}").do(play_mp3, folder_path, media_file)

    # Sort the jobs by their scheduled date and time
    schedule.jobs.sort(key=lambda x: x.next_run)

    # Print the first 50 scheduled events
    print_first_50_scheduled_events()
    print('')

    playback_thread = threading.Thread(target=play_media_files_in_loop, daemon=True)
    playback_thread.start()

    while True:
        time.sleep(1)


# Run the script
schedule_playback()
