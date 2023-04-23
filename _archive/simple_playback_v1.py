# simplest working version that loops through a folder and plays each file once


import vlc
import os

# Define variables
folder_path = 'timmy_sounds'

# Print list of files
media_files = [f for f in os.listdir(folder_path) if f.endswith('.mp3')]
print(f"Files in {folder_path}:")
for f in media_files:
    print(f)

# Play mp3 files
for media_file in media_files:
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

# Cleanup
player.stop()
instance.release()
