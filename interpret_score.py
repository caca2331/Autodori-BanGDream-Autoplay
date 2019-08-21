"""
Autodori: BanG Dream auto player
By caca2331

def interpret_score(score_name):

Will look at the score file named <score_name>.txt in the score directory.
Interpret the song score file into script friendly json file.
Output file name will be <original_file_name_without_.txt>_interpreted.json, in interpreted_score directory

Output Example:
[[ timeOfAction, locationOfAction, fingerID, actionType ], ...]

    timeOfAction:       in seconds
    locationOfAction:   1-7, from left to right in the game
    fingerID:           0-9, used to identify long bars.
    actionType:         1: touch down and up
                        2: touch down and up with flick
                        3: touch down (long bar)
                        4: node (long bar)
                        5: touch up (long bar)
                        6: touch up with flick (long bar)

Note:
Output is sorted in timeOfAction.

Usage as a individual call:
python3 interpret_score.py [file_name]
"""

import re
import json
from sys import argv


def interpret_score(score_name, print_result=False):
    score = []
    music_info = {}
    note_info = {}
    timed_actions = []

    # The majority of this function is adapted from https://github.com/yp05327/BangScoreMaker/ by yp05327
    # analysis score
    def init_score():
        music_info_key_word = {
            'bpm': '#BPM (\\d*)',
            'id': '#WAV01 bgm(\\d*).wav',
        }
        file_object = open('score/' + score_name + '.txt', 'r')
        read_step = 0
        try:
            for line in file_object:

                if read_step == 0:
                    # get music info
                    for key_word in music_info_key_word:
                        info = re.match(music_info_key_word[key_word], line)
                        if info:
                            music_info[key_word] = info.group(1)

                if read_step < 2:
                    # get note info
                    info = re.match('#WAV(\\d\\w) (\\w*).wav', line)
                    if info:
                        if read_step == 0:
                            read_step = 1
                        note_info[info.group(1)] = info.group(2)

                # get music score
                if line == '*---------------------- MAIN DATA FIELD\n':
                    read_step = 2
                    continue

                if read_step == 2:
                    info = re.match('#(\\d\\d\\d)(\\d)(\\d):(\\w*)', line)

                    if info:
                        score.append([
                            info.group(1),  # unitId
                            info.group(2),  # type
                            info.group(3),  # row
                            info.group(4)  # list
                        ])
        finally:
            file_object.close()

    def interpret():
        v = [False for _temp in range(9)]  # vertical slide
        for u in score:

            four_beat = int(u[0])

            # type of note.
            # 0: command, ignore
            # 1: normal note / non-vertical slide
            # 5: vertical slide
            note_type = int(u[1])

            # which track?
            # 6:   left most track in the game
            # 1-5: track 2-6 in the game (the center five)
            # 8:   right most track in the game
            track = int(u[2])
            # modified into 1-7 from left to right:
            track = 1 if track == 6 else (7 if track == 8 else (track - 1))

            # type of the note, and when the note falls
            pattern = u[3]

            # note type 0: command note (no real use)
            if note_type == 0:
                continue

            beat_per_division = 4 / (len(pattern) / 2.0)
            token = ""
            for i in range(len(pattern)):
                # extract two chars as a token
                if i % 2 == 0:
                    token = pattern[i]
                    continue
                else:
                    token += pattern[i]

                # skip token if it is not recognized. otherwise re-assign its value (note_type string)
                if token not in note_info:
                    continue
                else:
                    token = note_info[token]

                # generate time_offset and touch_loc based on current token
                time_offset = (four_beat * 4 + i // 2 * beat_per_division) * 60.0 / int(music_info["bpm"])

                # vertical slide
                if note_type == 5:
                    if not v[track]:
                        timed_actions.append([time_offset, track, track, 3])
                        v[track] = True
                    else:
                        timed_actions.append(
                            [time_offset, track, track, 5 if token in ["flick", "fever_note_flick"] else 6])
                        v[track] = False

                # single note, or non-vertical slide
                else:
                    if token in ["bd", "skill", "fever_note"]:
                        timed_actions.append([time_offset, track, 0, 1])
                    elif token in ["flick", "fever_note_flick"]:
                        timed_actions.append([time_offset, track, 0, 2])

                    elif token in ["slide_a"]:
                        timed_actions.append([time_offset, track, 8, 3 if v[0] else 4])
                        v[0] = True
                    elif token in ["slide_b"]:
                        timed_actions.append([time_offset, track, 9, 3 if v[8] else 4])
                        v[8] = True

                    elif token in ["slide_end_a", "slide_end_flick_a"]:
                        timed_actions.append([time_offset, track, 8, (5 if token in ["slide_end_flick_a"] else 6)])
                        v[0] = False
                    elif token in ["slide_end_b", "slide_end_flick_b"]:
                        timed_actions.append([time_offset, track, 9, (5 if token in ["slide_end_flick_b"] else 6)])
                        v[8] = True

    def write_to_file():
        with open('interpreted/' + score_name + '_interpreted.json', 'w') as f:
            json.dump(timed_actions, f)

    def print_timed_actions():
        for action in timed_actions:
            print(action)

    init_score()
    interpret()
    list.sort(timed_actions)
    print_timed_actions()
    write_to_file()
    if print_result:
        print_timed_actions()


if __name__ == "__main__":
    interpret_score(*argv[1:])

