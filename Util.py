import subprocess
import random
import time


#
class DeviceInfo:
    def __init__(self):
        sp = subprocess.Popen(["./adb", "shell", "wm", "size"], stdout=subprocess.PIPE)
        sp.wait()

        info = str(sp.stdout.readline()).split()[2]
        if "\\n" in info:
            info = info[:len(info) - 3]
        x_loc = info.index("x")
        self.w, self.h = int(info[:x_loc]), int(info[x_loc + 1:])

        self.track_loc = [
            None,
            (self.w * 240.7 / 1136.0, self.h * 505 / 640.0, self.w * 370.7 / 1136.0, self.h * 545 / 640.0),
            (self.w * 371.3 / 1136.0, self.h * 505 / 640.0, self.w * 501.3 / 1136.0, self.h * 545 / 640.0),
            (self.w * 502.0 / 1136.0, self.h * 505 / 640.0, self.w * 632.0 / 1136.0, self.h * 545 / 640.0),
            (self.w * 632.7 / 1136.0, self.h * 505 / 640.0, self.w * 762.7 / 1136.0, self.h * 545 / 640.0),
            (self.w * 763.3 / 1136.0, self.h * 505 / 640.0, self.w * 893.3 / 1136.0, self.h * 545 / 640.0),
            (self.w * 110.0 / 1136.0, self.h * 505 / 640.0, self.w * 240.0 / 1136.0, self.h * 545 / 640.0),
            None,
            (self.w * 894.0 / 1136.0, self.h * 505 / 640.0, self.w * 1024 / 1136.0, self.h * 545 / 640.0),
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


class ImgProcess:
    def __init__(self):
        pass

    @staticmethod
    def screenshot():
        # subprocess.Popen
        subprocess.run(["adb", "shell", "screencap", "-p", ">cap.png"])


def run_cmd(cmd):
    # if len(cmd)==7:
    subprocess.Popen(cmd, stdout=subprocess.PIPE)


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
        dx = (xx2 - xx1) / 200.0
        ctr = 0
        while random.random() > .05:
            ctr += 1
        if ctr > 100:
            ctr = 0
        return xx1 + dx * (100 + (ctr if random.random() < .5 else - ctr))

    return centered_loc(x1, x2), centered_loc(y1, y2)


# assuming a 0.05 second stick on the screen after touching it
def rand_time_for_touch(expected_time=0.05):
    # 50% 0.8-1 40%1-1.5 10& 1.5-2
    if random.random() < .5:
        return random.uniform(.8, 1) * expected_time
    if random.random() < .8:
        return random.uniform(1, 1.5) * expected_time
    return random.uniform(1.5, 2) * expected_time

# def
