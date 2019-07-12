import random
from util import *

#
# This file process the song data and plays the song
#

simpleRandomMove = True
complicateRandomMove = False
randomTimeDelay = True

# normal good player(fc lv25 songs) will be 10,
# 20 will be very good player,
# 25 will be top 10 player,
# 30+ will be suspicious (risky!)
myLv = 10
# if actual_song_lv_in_the_game <= 20, songLv = 0
# else songLv = actual_song_lv_in_the_game - 20
songLv = 10

p_perfect = 85 + 15 * (1 - .8 ** myLv * 1.2 ** songLv)
great_miss_ratio = myLv / 1.2 ** songLv
# (40% 0-0.3 21% 0.3-0.5 19% 0.5-0.7 18% 0.72-0.95 2% 0.95-1) * p_perfect
# (40% 1-) * p_great
# () * p_miss


# 数据(range in miliseconds for perfect)
# (暂时都按40处理)
touch_s = -40  # start
touch_e = 40  # end

songData = None

# tuple: touch type
event = []


def gen_touch(x, y):
    touch(x, y)
    pass


def gen_move(x1, y1, x2):
    pass


def initSongData(songName):
    pass


def startAutoPlay():
    pass
