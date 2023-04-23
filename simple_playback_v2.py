# simplest working version that loops through a folder and plays each file once
# adds a schedule.  Schedule does not work quite right though and only playes files once per play_period


import vlc
import os
import schedule
import time

# print system time as a debug measure
print(f"Current time: {time.strftime('%H:%M:%S')}")

# Define variables
#folder_path = 'bird_calls'
folder_path = 'timmy_sounds'
playback_schedule = [
    ("00:00", "01:00"),
    ("06:00", "09:00"),
    ("12:00", "17:00"),
    ("18:00", "21:00")
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
def play_mp3(folder_path, media_file):
    instance = vlc.Instance('--aout=alsa')
    player = instance.media_player_new()
    media = instance.media_new(os.path.join(folder_path, media_file))
    player.set_media(media)
    player.play()
    print(f"Now playing: {media_file}")
    while True:
        state = player.get_state()
        if state == vlc.State.Ended:
            break
    player.stop()
    instance.release()

import datetime

def schedule_playback():
    now = datetime.datetime.now()
    for start_time, stop_time in playback_schedule:
        print('')
        print('start = '+start_time+' stop = '+stop_time)

        start_hour, start_minute = map(int, start_time.split(':'))
        stop_hour, stop_minute = map(int, stop_time.split(':'))
        scheduled_start_time = now.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
        scheduled_stop_time = now.replace(hour=stop_hour, minute=stop_minute, second=0, microsecond=0)

        if scheduled_stop_time <= scheduled_start_time:
            scheduled_stop_time += datetime.timedelta(days=1)

        if scheduled_start_time <= now < scheduled_stop_time:
            for media_file in media_files:
                print(media_file)
                play_mp3(folder_path, media_file)
        else:
            if scheduled_start_time <= now:
                scheduled_start_time += datetime.timedelta(days=1)

            for media_file in media_files:
                print(media_file)
                schedule.every().day.at(scheduled_start_time.strftime('%H:%M')).do(play_mp3, folder_path, media_file)

    while True:
        # Sort the jobs by their scheduled date and time
        schedule.jobs.sort(key=lambda x: x.next_run)

        for job in schedule.jobs:
            print(f"Job '{job.job_func.__name__}' scheduled at {job.next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        schedule.run_pending()
        time.sleep(1)


# Run the script
schedule_playback()
