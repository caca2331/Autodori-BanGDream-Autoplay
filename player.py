import random
from util import *
from img_processor import *
import re
import sys
import threading
import time

#
# This file process the song data and plays the song
#


complicateRandomMove = False
randomTimeDelay = True

global_delay = 0

# normal good player(fc lv25 songs) will be 10,
# 20 will be very good player,
# 25 will be top 10 player,
# 30+ will be suspicious (risky!)
myLv = 10
# if actual_song_lv_in_the_game <= 20, songLv = 0
# else songLv = actual_song_lv_in_the_game - 20
songLv = 10

''' inner vars '''

p_perfect = 85 + 15 * (1 - .8 ** myLv * 1.2 ** songLv)
great_miss_ratio = myLv / 1.2 ** songLv
# (40% 0-0.3 21% 0.3-0.5 19% 0.5-0.7 18% 0.72-0.95 2% 0.95-1) * p_perfect
# (50% 1-1.4 35% 1.4-1.7 10% 1.7-1.95 5% 1.95-2.0) * p_great
# (60% 2-3.5, miss otherwise) * p_miss


# note data (range in milliseconds for perfect)
note_time_range = {
    ('skill', 1): (-33, 50),
    'bd': (-33, 50),
    'flick': (-33, 50),
    'fever_note': (),
    '': ()
}
track_loc_data = []


def init_track_loc_data(w, h):
    track_loc_data = [
        # (w *, h *, w *, h *),
        # (w *, h *, w *, h *),
        # (w *, h *, w *, h *),
        # (w *, h *, w *, h *),
        # (w *, h *, w *, h *),
        # (w *, h *, w *, h *),
        # None,
        # (w *, h *, w *, h *)
    ]


# The majority of this function is derived from https://github.com/yp05327/BangScoreMaker/ by yp05327
# analysis song
def init_score(song_name):
    music_info_key_word = {
        'bpm': '#BPM (\\d*)',
        'id': '#WAV01 bgm(\\d*).wav',
    }

    file_object = open('score/' + song_name, 'rU')

    score = []
    music_info = {}
    note_info = {}

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

    return score, music_info, note_info


'''
checklist:
long that covers multiple 4 
pink
'''


# convert score into timestamped actions
def init_timestamped_actions(score, note_info, music_info):
    """
    types of misses:
    single touch:
        totally misses a note
        touched too early or late
        didn't slide on flick
    bar:
        missed first one
        didn't get in position on time in slide
        release too early
        didn't slide on flick


    implementation v0:
    single touch:
        can only have all type
    bar:
        last one release too early

    """

    def gen_time_offset():
        if not randomTimeDelay:
            local_offset = 0
        else:
            local_offset = 0
            #     # for now, assume both bound are 40, and has same probably to go beyond each
            #     l, h = -40, 40  # lower bound, upper(high) bound
            #     if random.random() < p_perfect:
            #         # (40% 0-0.3 21% 0.3-0.5 19% 0.5-0.72 18% 0.72-0.95 2% 0.95-1) * p_perfect
            #         r = random.random()  # range
            #         if r < .4:
            #             local_offset = random.random(0, .3) * h
            #         elif r < .61:
            #             local_offset = random.uniform(.3, .5) * h
            #         elif r < .8:
            #             local_offset = random.uniform(.5, .72) * h
            #         elif r < .98:
            #             local_offset = random.uniform(.72, .95) * h
            #         else:
            #             local_offset = random.uniform(.95, .1) * h
            #     elif great_miss_ratio < random.uniform(0, 1 + great_miss_ratio):
            #     # (50% 1-1.4 35% 1.4-1.7 10% 1.7-1.95 5% 1.95-2.0) * p_great
            #     # (60% 2-3.5, miss otherwise) * p_miss
            #     else:

            if random.random < .5:
                local_offset = -local_offset

        result = (four_beat * 4 + i // 2 * beat_per_division) * music_info["bpm"] + local_offset
        return result if result > 0 else 0

    def gen_touch_loc():
        x1, x2, y1, y2 = track_loc_data[track]
        return rand_loc(x1, x2, y1, y2), rand_loc(x1, x2, y2 + y2 - y1, y1)

    timestamped_actions = []

    a = []  # slide a
    b = []  # slide b
    v = [None, None, None, None, None, None, None, None]  # vertical slide
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

        # type of the note, and when the note falls
        pattern = u[3]

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

            if token not in note_info:
                token = ""
                continue
            else:
                token = note_info[token]

            if note_type == 5:  # vertical slide
                if v[track] is None:  # start of vertical slide
                    v[track] = gen_time_offset(), gen_touch_loc()
                else:  # end of vertical slide
                    timestamped_actions.append((v[track][0], gen_move(
                        v[track][1] + gen_touch_loc() + (gen_time_offset() - v[track][0],))))
                    v[track] = None

            # if
            token = ""
        #     if token ==
        #
        # while len(u[3]) > 2 ** divisor * 2:
        #     divisor += 1
        #
        # if u[1] == 1:

    return timestamped_actions


def start_auto_play(timestamped_actions):
    begin = time.time()
    for time_offset, command in timestamped_actions:

        if time.time() < time_offset + begin:
            time.sleep(time_offset + begin - time.time())
        run_cmd(command)


# debug use main
if __name__ == "__main__":
    score, a, b = init_score("yes_bang_dream_easy.txt")
    print(a)
    print("*********************")
    print(b)
    print("*********************")
    print(score)
