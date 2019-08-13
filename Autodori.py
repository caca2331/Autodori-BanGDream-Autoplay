"""
Autodori: BanG Dream auto player
By caca2331

Class ScoreInterpreter:
Interpret the txt song score file into script friendly json file.
Output file name will be <original_file_name_without_.txt>_interpreted.json

Output Example:
[[ timeOfAction, locationOfAction, fingerID, actionType ], ...]

    timeOfAction:       in seconds
    locationOfAction:   1-7, from left to right in the game
    fingerID:           1 or 2, used to identify long bars.
    actionType:         1: touch down and up
                        2: touch down and up with flick
                        3: touch down (long bar)
                        4: node (long bar)
                        5: touch up (long bar)
                        6: touch up with flick (long bar)

Note:
Output is sorted in timeOfAction.
"""


class ScoreInterpreter:
    pass
