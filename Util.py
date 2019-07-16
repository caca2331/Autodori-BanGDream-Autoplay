import subprocess
import random


#
class DeviceInfo:
    def __init__(self):
        self.w, self.h = subprocess.run(["adb", "shell", "wm", "size"])  # TODO
        self.track_loc = [
            # (w *, h *, w *, h *),
            # (w *, h *, w *, h *),
            # (w *, h *, w *, h *),
            # (w *, h *, w *, h *),
            # (w *, h *, w *, h *),
            # (w *, h *, w *, h *),
            # None,
            # (w *, h *, w *, h *)
        ]

        self.layer1_perform_loc = 0
        self.layer2_free_live_loc = 0
        self.layer2_1_multilive_loc = 0
        self.layer2_2_multilive_room_choosing_loc = 0
        self.layer3_song_choosing_rdy_loc = 0
        self.layer3_prev_song_loc = 0
        self.layer3_next_song_loc = 0
        self.layer4_perform_rdy_loc = 0
        self.layer5_score_confirm_loc = 0
        self.layer6_rank_up_loc = 0


def run_cmd(cmd):
    subprocess.run(cmd)


def screenshot():
    subprocess.run(["adb", "shell", "screencap", "-p", ">cap.png"])


# TODO: confirm delay from adb to phone
def gen_move(x1, y1, x2=None, y2=None, duration=0.01, prev=None):
    """
    only x1, y1:
    """
    if x2 is None:
        return ["adb", "shell", "input", "", x1, y1, x1, y1, str(duration)]
    if prev is None:
        return ["adb", "shell", "input", "", x1, y1, x2, y2, str(duration), ]
    return prev + []


# more likely to be centered
def rand_loc(x1, y1, x2, y2):
    def centered_loc(xx1, xx2):
        dx = (xx2 - xx1) / 200
        ctr = 0
        while random.random > .05:
            ctr += 1
        if ctr > 20:
            ctr = 0
        return xx1 + (dx * ctr if random.random() < .5 else -dx * ctr)

    return centered_loc(x1, x2), centered_loc(y1, y2)


def rand_time(expected_time):
    # 50% 0.5-1 40%1-2 10% 2-5
    if random.random < .5:
        return (0.5 + random.random / 2) * expected_time
    if random.random < .8:
        return (1 + random.random) * expected_time
    return random.uniform(2, 5) * expected_time
