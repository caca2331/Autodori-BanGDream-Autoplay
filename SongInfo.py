import re
import json
from sys import argv

from Util import *


#
# This file process the song data
#
#
#


class SongInfo:
    # constants used for song play generation
    F_DUR = 0.08  # expected duration of flick
    STICK_DUR = 0.05  # expected duration of a touch on the the screen
    SLIDE_STICK_DUR = 0.08  # min time for a finger to stay between two notes within a slide

    IN_AIR_DUR = 0.08  # min time for a finger to stay in air between two touches

    def __init__(self, song_name, screen_info=None, player_lv=None, sampling_period=None):
        self.song_name = song_name

        # by iOS default it should be 60Hz (except iPad pro of 120Hz)
        self.sampling_period = float(sampling_period) if sampling_period else 1.0 / 60

        self.screen_info = screen_info
        # self.global_delay = global_delay

        # normal good player(fc lv25 songs) will be 10,
        # 20 will be very good player,
        # 25 will be top 10 player,
        # 30+ will be suspicious (risky!)
        self.player_lv = int(player_lv) if player_lv else 10

        # if actual_song_lv_in_the_game <= 20, difficulty = 0
        # else difficulty = actual_song_lv_in_the_game - 20
        self.difficulty = 10

        # (40% 0-0.3 21% 0.3-0.5 19% 0.5-0.7 18% 0.72-0.95 2% 0.95-1) * p_perfect
        # (50% 1-1.4 35% 1.4-1.7 10% 1.7-1.95 5% 1.95-2.0) * p_great
        # (60% 2-3.5, miss otherwise) * p_miss
        self.p_perfect = .85 + .15 * (1 - .8 ** self.player_lv * 1.2 ** self.difficulty)
        self.great_miss_ratio = self.player_lv / 1.2 ** self.difficulty

        self.score = []
        self.music_info = {}
        self.note_info = {}
        self.timed_actions = []

        ''' constants '''
        # note data (range in milliseconds for perfect)
        self.note_time_range = {
            ('skill', 1): (-33, 50),
            'bd': (-33, 50),
            'flick': (-33, 50),
            'fever_note': (),
            '': ()
        }
        # delay between when song poster disappear and song begin to play
        # self._post_poster_delay =

    # The majority of this function is adapted from https://github.com/yp05327/BangScoreMaker/ by yp05327
    # analysis song
    def init_score(self):
        music_info_key_word = {
            'bpm': '#BPM (\\d*)',
            'id': '#WAV01 bgm(\\d*).wav',
        }

        file_object = open('score/' + self.song_name + '.txt', 'r')

        read_step = 0
        try:
            for line in file_object:
                if read_step == 0:
                    # get music info
                    for key_word in music_info_key_word:
                        info = re.match(music_info_key_word[key_word], line)
                        if info:
                            self.music_info[key_word] = info.group(1)

                if read_step < 2:
                    # get note info
                    info = re.match('#WAV(\\d\\w) (\\w*).wav', line)
                    if info:
                        if read_step == 0:
                            read_step = 1
                        self.note_info[info.group(1)] = info.group(2)

                # get music score
                if line == '*---------------------- MAIN DATA FIELD\n':
                    read_step = 2
                    continue

                if read_step == 2:
                    info = re.match('#(\\d\\d\\d)(\\d)(\\d):(\\w*)', line)

                    if info:
                        self.score.append([
                            info.group(1),  # unitId
                            info.group(2),  # type
                            info.group(3),  # row
                            info.group(4)  # list
                        ])
        finally:
            file_object.close()

    # convert score into timestamped actions
    def init_timed_actions(self):
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

        # time offset from the beginning of the song to the time when teh action should be performed
        def gen_time_offset():
            if not randomTimeDelay:
                local_offset = 0
            else:

                # for now, assume both bound are 40, and has same probably to go beyond each
                l, h = -40, 40  # lower bound, upper(high) bound
                if random.random() < self.p_perfect:
                    # (40% 0-0.3 21% 0.3-0.5 19% 0.5-0.72 18% 0.72-0.95 2% 0.95-1) * p_perfect
                    r = random.random()  # range
                    if r < .4:
                        local_offset = random.random(0, .3) * h
                    elif r < .61:
                        local_offset = random.uniform(.3, .5) * h
                    elif r < .8:
                        local_offset = random.uniform(.5, .72) * h
                    elif r < .98:
                        local_offset = random.uniform(.72, .95) * h
                    else:
                        local_offset = random.uniform(.95, .1) * h
                elif self.great_miss_ratio < random.uniform(0, 1 + self.great_miss_ratio):
                    pass
                # (50% 1-1.4 35% 1.4-1.7 10% 1.7-1.95 5% 1.95-2.0) * p_great
                # (60% 2-3.5, miss otherwise) * p_miss
                else:
                    pass

            if random.random() < .5:
                local_offset = -local_offset

            result = (four_beat * 4 + i // 2 * beat_per_division) * 60.0 / int(self.music_info["bpm"]) + local_offset
            return result if result > 0 else 0

        # generate a random location on a track
        def gen_touch_loc(flick=False):
            x1, x2, y1, y2 = self.screen_info.track_loc[track]
            if flick:
                return rand_loc(x1, x2, y1 + y1 + y1 - y2 - y2, y1 + y1 - y2)
            return rand_loc(x1, x2, y1, y2)

        # create continuous touch by multiple individual call with adb
        def add_touch_cmd(action_list, finish_with_flick=False):
            touch_command_list = []
            time_offset, (x, y) = action_list[0]
            # single touch
            if len(action_list) == 1:
                if finish_with_flick:  # finger sticks on screen for 0.15s while flicking
                    x2, y2 = gen_touch_loc(True)
                    touch_command_list.append([x, y, x2, y2, rand_time_for_touch(SongInfo.F_DUR)])
                else:
                    x2, y2 = rand_loc(x - 5, y - 5, x + 5, y + 5)
                    touch_command_list.append([x, y, x2, y2, rand_time_for_touch(SongInfo.STICK_DUR)])

            # bar / slide
            else:
                for i in range(1, len(action_list)):
                    time_offset2, (x2, y2) = action_list[i]
                    if time_offset + SongInfo.SLIDE_STICK_DUR > time_offset2:
                        time_offset2 = time_offset + SongInfo.SLIDE_STICK_DUR

                    touch_command_list.append([x, y, x2, y2, time_offset2 - time_offset])

                    time_offset, x, y = time_offset2, x2, y2

                if finish_with_flick:  # finger sticks on screen for 0.15s while flicking
                    x2, y2 = gen_touch_loc(True)
                    touch_command_list.append([x, y, x2, y2, rand_time_for_touch(SongInfo.F_DUR)])

            timed_actions_without_id.append((action_list[0][0], touch_command_list))

        self.timed_actions = []
        timed_actions_without_id = []  # reset

        slide_a, slide_b = [], []  # slide a, slide b

        v = [[] for _temp in range(9)]  # vertical slide
        for u in self.score:

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

                # skip token if it is not recognized. otherwise re-assign its value (note_type string)
                if token not in self.note_info:
                    continue
                else:
                    token = self.note_info[token]

                # generate time_offset and touch_loc based on current token
                temp_cmd_of_token = gen_time_offset(), gen_touch_loc()

                # vertical slide
                if note_type == 5:
                    v[track].append(temp_cmd_of_token)
                    if len([track]) == 2:  # end of vertical slide
                        add_touch_cmd(v[track], token in ["flick", "fever_note_flick"])
                        v[track] = []

                # single note, or non-vertical slide
                else:
                    if token in ["bd", "skill", "fever_note"]:
                        add_touch_cmd([temp_cmd_of_token])
                    elif token in ["flick", "fever_note_flick"]:
                        add_touch_cmd([temp_cmd_of_token], True)

                    elif token in ["slide_a"]:
                        slide_a.append(temp_cmd_of_token)
                    elif token in ["slide_b"]:
                        slide_b.append(temp_cmd_of_token)

                    elif token in ["slide_end_a", "slide_end_flick_a"]:
                        slide_a.append(temp_cmd_of_token)
                        add_touch_cmd(slide_a, token in ["slide_end_flick_a"])
                        slide_a = []
                    elif token in ["slide_end_b", "slide_end_flick_b"]:
                        slide_b.append(temp_cmd_of_token)
                        add_touch_cmd(slide_b, token in ["slide_end_flick_b"])
                        slide_b = []

        ''' *** *** '''
        list.sort(timed_actions_without_id)
        finger = [-1, -1]  # the latest time that either finger is touched down (finger0 and finger1)
        for start_time, actions in timed_actions_without_id:
            # determine which finger to use
            # if finger0 not in use, use it.
            if finger[0] + SongInfo.IN_AIR_DUR <= start_time:
                finger_to_use = 0
            # else if finger1 not in use, use it.
            elif finger[1] + SongInfo.IN_AIR_DUR <= start_time:
                finger_to_use = 1
            # else use whichever finger that is available sooner.
            elif finger[1] + SongInfo.IN_AIR_DUR <= finger[0]:
                finger_to_use = 1
                start_time = min(finger) + SongInfo.IN_AIR_DUR
            else:
                finger_to_use = 0
                start_time = min(finger) + SongInfo.IN_AIR_DUR

            ttl_dur = 0
            for i in range(len(actions)):
                # format: [ [time_in_sec, finger_id, x1, y1, x2, y2, duration_in_sec,
                #            is_start_with_finger_attached(1 or 0), is_end_with_finger_attached(1 or 0)] ... ]
                self.timed_actions.append([start_time + ttl_dur, finger_to_use,
                                           round(actions[i][0]), round(actions[i][1]),
                                           round(actions[i][2]), round(actions[i][3]), actions[i][4],
                                           0 if i == 0 else 1, 0 if i == len(actions) - 1 else 1])
                ttl_dur += actions[i][4]

            finger[finger_to_use] = start_time + ttl_dur

    # write timestamped commands to a json file.
    # format 1: [ [time_in_sec, finger_id, x1, y1, x2, y2, duration_in_sec,
    #            is_start_with_finger_attached(1 or 0), is_end_with_finger_attached(1 or 0)] ... ]
    # format 2: [ [time_in_sec, finger_id, x, y, finger_attaching/moving/leaving(0/1/2)], ... ]
    def write_to_file(self, name=None):
        if name is None:
            name = self.song_name + '-timed_actions'
        with open('build/' + name + '.json', 'w') as f:
            json.dump(self.timed_actions, f)

    def transform_timed_actions_type(self, timed_actions_type=None):
        if timed_actions_type == 1:
            transformed_timed_actions = []

            for s_time, f_id, x1, y1, x2, y2, dur, is_s_attached, is_e_attached in self.timed_actions:
                print(s_time, f_id, x1, y1, x2, y2, dur, is_s_attached, is_e_attached)
                if not is_s_attached:
                    transformed_timed_actions.append([s_time, f_id, x1, y1, 0])

                time_sep = dur / self.sampling_period
                dx, dy = (x2 - x1) / time_sep, (y2 - y1) / time_sep

                while time_sep > 1:
                    s_time += self.sampling_period
                    x1 += dx
                    y1 += dy
                    time_sep -= 1
                    transformed_timed_actions.append([s_time, f_id, x1, y1, 1])

                s_time += time_sep * self.sampling_period
                transformed_timed_actions.append([s_time, f_id, x2, y2, 1])
                if not is_e_attached:
                    transformed_timed_actions.append([s_time, f_id, x2, y2, 2])

            list.sort(transformed_timed_actions)
            self.timed_actions = transformed_timed_actions

    @staticmethod
    def gen_timed_actions(song_name, w, h, player_lv=None, filename=None, timed_actions_type=0,
                          sampling_period=None):
        song = SongInfo(song_name, ScreenInfo(w, h), player_lv, sampling_period)
        song.init_score()
        song.init_timed_actions()
        song.transform_timed_actions_type(int(timed_actions_type))
        song.write_to_file(filename)


if __name__ == "__main__":
    print("Usage: song_name, [screen width] [screen height] [player_lv]"
          "song_name is the name of the score file in score directory, without the suffix of '.txt'"
          "screen width")
    SongInfo.gen_timed_actions(*argv[1:])
