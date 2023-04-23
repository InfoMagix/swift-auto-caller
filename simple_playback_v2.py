# v1_simplest working version that loops through a folder and plays each file once
# v2_ added a schedule
import vlc
import os
import schedule
import time

# pritn system time as a debug measure
print(f"Current time: {time.strftime('%H:%M:%S')}")


# Define variables
folder_path = 'bird_calls'
playback_schedule = [
    ("00:00", "01:00"),
    ("06:00", "09:00"),
    ("12:00", "15:00"),
    ("18:00", "21:00")
]

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


def schedule_playback():
    for start_time, stop_time in playback_schedule:
        print('')
        print('start = '+start_time+' stop = '+stop_time)

        for media_file in media_files:
            print(media_file)
            schedule.every().day.at(start_time).do(play_mp3, folder_path, media_file)
            
    while True:
        for job in schedule.jobs:
            print(f"Job '{job.job_func.__name__}' scheduled at {job.next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        schedule.run_pending()
        time.sleep(1)

# Run the script
schedule_playback()
