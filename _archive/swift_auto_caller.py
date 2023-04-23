import vlc
import os
import schedule
import time

# Declare variables
folder_path = 'bird_calls'
playback_schedule = [
    ("00:00", "01:00"),
    ("06:00", "09:00"),
    ("12:00", "15:00"),
    ("18:00", "21:00")
]

print(folder_path)

# Define functions
def play_mp3(folder_path):
    media_files = [f for f in os.listdir(folder_path) if f.endswith('.mp3')]
    #instance = vlc.Instance('--aout=alsa')
    instance = vlc.Instance('--aout=alsa --alsa-audio-device="hw:0,0"')
    instance = vlc.Instance('--aout=alsa', '--alsa-audio-device=hw:0,0')

    player = instance.media_list_player_new()
    media_list = instance.media_list_new([os.path.join(folder_path, f) for f in media_files])
    player.set_media_list(media_list)
    player.play()
    return player

def schedule_playback(folder_path, playback_schedule):
    player = None

    for start_time, stop_time in playback_schedule:
        schedule.every().day.at(start_time).do(lambda: (player.stop() if player else None), player=play_mp3(folder_path))
        schedule.every().day.at(stop_time).do(lambda: player.stop() if player else None)

    while True:
        schedule.run_pending()
        time.sleep(1)

# Run the script
schedule_playback(folder_path, playback_schedule)
