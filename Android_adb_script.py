from SongInfo import *


def start_auto_play(timed_actions):
    begin = time.time()
    for time_offset, command in timed_actions:
        print(time_offset, command, time.ctime())
        if time.time() < time_offset + begin:
            time.sleep(time_offset + begin - time.time())
        run_cmd(["./adb", "shell"] + command)


def get_resolution():
    sp = subprocess.Popen(["./adb", "shell", "wm", "size"], stdout=subprocess.PIPE)
    sp.wait()

    info = str(sp.stdout.readline()).split()[2]
    if "\\n" in info:
        info = info[:len(info) - 3]
    x_loc = info.index("x")
    return int(info[:x_loc]), int(info[x_loc + 1:])


usage = "Usage:\n" \
        "Help        help, show this page\n" \
        "Set         manually set song name that will be played next\n" \
        "Play        (after set a song) play song for a single time\n" \
        "Delay       (after set a song) set delay of key\n" \
        "AutoDelay   (after set a song) (in development)\n" \
        "            Go to settings and in the delay setting page, run this command\n" \
        "Cycle       (after set a song) Fully automated, plays the song for cycle of times.\n" \
        "Quit        quit program\n"

screen = ScreenInfo()

print(usage)
global_delay = 0
lv = 10
song = SongInfo()

while True:
    cmd = input("Enter your command (initial is OK): ")
    print(cmd)
    if len(cmd) == 0:
        continue
    elif cmd[0] in ["h", "H", "help", "Help"]:
        print(usage)

    elif cmd[0] in ["s", "S", "set", "Set"]:
        # song_name = input("Enter song name:")
        song_name = "128_ichiyamonogatari_expert.txt"
        song = SongInfo(song_name, screen)
        song.init_score()
        song.init_timed_actions()

    elif cmd[0] in ["o"]:
        song.write_to_file()

    elif cmd[0] in ["d", "D", "delay", "Delay"]:
        entered_delay = input("Enter delay:")
        song.global_delay = int(entered_delay)

    elif cmd[0] in ["ad", "AD", "autodelay", "AutoDelay"]:
        in_game_delay = input("Enter the delay info showed in the game:")
        pass

    elif cmd[0] in ["q", "Q", "quit", "Quit"]:
        break

    else:
        print("else")
        print(song.timed_actions)
        for temp in song.timed_actions:
            print(temp)
