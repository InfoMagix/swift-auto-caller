import vlc

instance = vlc.Instance('--no-xlib')
player = instance.media_player_new()
media = instance.media_new('http://www.hochmuth.com/mp3/Haydn_Cello_Concerto_D-1.mp3')
player.set_media(media)
player.play()

while True:
    pass

