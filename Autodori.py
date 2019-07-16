"""
Autodori: BanG Dream auto player
By caca2331
"""

from Util import *
from SongInfo import *

device = DeviceInfo()

usage = "Usage:\n" \
        "Help             help, show this page\n" \
        "Set [song_name]  manually set song_name that will be played next\n" \
        "Play             (after set a song) play song for a single time\n" \
        "Delay [delay]    (after set a song) set delay of key\n" \
        "Quit             quit program\n"

print(usage)
while True:
    command = input("Enter your command (initial is OK): ").split()
    song = None
    if len(command) == 0:
        continue
    elif command[0] in ["h", "H", "help", "Help"]:
        print(usage)

    elif command[0] in ["p", "P", "play", "Play"]:
        song.start_auto_play()

    elif command[0] in ["q", "Q", "quit", "Quit"]:
        break

    elif command[0] in ["d", "D", "delay", "Delay"]:
        song.global_delay = int(command[1])

    elif command[0] in ["s", "S", "set", "Set"]:
        song = SongInfo(command[1], device)

    else:
        print("\nUnknown command")
        print(usage)
