socket = require("socket")


--[[ ********** #MARK global variables ********** ]]

-- paths
score_dir_path = "/var/mobile/Library/AutoTouch/Scripts/Autodori/score"
intepreted_score_dir_path = "/var/mobile/Library/AutoTouch/Scripts/Autodori/interpreted"
playable_dir_path = "/var/mobile/Library/AutoTouch/Scripts/Autodori/playable"
-- config
is_random_song = nil
is_multi_mode = nil
remaining_loop = nil
lv = nil

-- width and height of the screen
w = nil
h = nil
-- '4:3' or '16:9'
device_type = nil
-- sampling period of screen, used to calucuate # of move event generated. In seconds.
sampling_period = nil
-- key: name of the specific area; value: x,y of the top left corner and bottom-right corner
btns = nil
-- { name_of_area:{{x,y,color}, ...  }, ...}
key_pixels = nil
-- touch actions to be performed
actions = nil


--[[ ********** #MARK debugging ********** ]]

function print_actions(actions)
    for i = 1, #actions, 5 do
        print(actions[i], actions[i + 1], actions[i + 2], actions[i + 3], actions[i + 4])
    end
end

-- get color of pixels in the given area
function get_color(area_to_check)
    for i in 0, 100 do

        log() --todo
    end
end

function linux_main()
    w, h = 2224, 1668

    device_type = init_device_type()
    sampling_period = init_sampling_period()

    btns = init_btns()
    key_pixels, key_pixels_color = init_key_pixels()

    math.randomseed(os.time())

    is_random_song, is_multi_mode, remaining_loop = nil, nil, 1;
    lv = 10

    actions = init_actions_from_intepreted_score('')
    print_actions()
    os.exit(0)
end


--[[ ********** #MARK initialization ********** ]]

-- identify which device it is
function init_device_type()
    if w == 2224 or w == 2732 or w == 2048 then
        return '4:3'
    elseif 1 then
        return '16:9'
    end
end

-- init sampling period based on the device
function init_sampling_period()
    if w == 2224 or w == 2732 then
        return 1 / 120 -- sampling period for iPad Pros are 1 / 120
    else
        return 1 / 60 -- for other devices, 1 / 60
    end
end

-- init locations for buttons in the UI
function init_btns()
    if device_type == '4:3' then
        local iPad_btns = {
            live = { 1, 2, 3, 4 },
            easy = { 1, 1, 5, 5 },
            p1 = { 215, 1200, 469, 1270 },
            p2 = { 470, 1200, 724, 1270 },
            p3 = { 726, 1200, 980, 1270 },
            p4 = { 982, 1200, 1236, 1270 },
            p5 = { 1237, 1200, 1491, 1270 },
            p6 = { 1492, 1200, 1746, 1270 },
            p7 = { 1748, 1200, 2006, 1270 }
        }
        local w_r, h_r = w / 2224, h / 1668

        for k, v in pairs(iPad_btns) do
            iPad_btns[k] = { v[1] * w_r, v[2] * h_r, v[3] * w_r, v[4] * h_r }
        end
        return iPad_btns
    end
end

-- init locations and initeger_color of pixels to check
function init_key_pixels()
    if device_type == '4:3' then
        local iPad_pixels = {
            live = {
                { 1, 2 }, { 3, 4 }
            },
            black_background = {
                { 100, 100 }, { 200, 100 }, { 300, 100 }, { 400, 100 }, { 500, 100 }, { 600, 100 }
            }
        }
        local iPad_pixels_color = {
            live = { 1, 2 },
            black_background = { 0, 0, 0, 0, 0, 0 }
        }
        local w_r, h_r = w / 2224, h / 1668
        for k, v in pairs(iPad_pixels) do
            for kk, vv in pairs(v) do
                v[kk] = { vv[1] * w_r, vv[2] * h_r }
                iPad_pixels[k] = v
            end
        end
        return iPad_pixels, iPad_pixels_color
    end
end

-- generate a ramdom playable score
function init_actions_from_intepreted_score(file)
    local F_DUR = 0.08 -- expected duration of flick
    local STICK_DUR = 0.05 -- expected duration of a touch on the the screen
    local SLIDE_STICK_DUR = 0.08 -- min time for a finger to stay between two notes within a slide

    local IN_AIR_DUR = 0.08 -- min time for a finger to stay in air between two touches
    local actions = {}
    --[[[[ timeOfAction, locationOfAction, fingerID, actionType ], ...]
    --
    --    timeOfAction:       in seconds
    --    locationOfAction:   1-7, from left to right in the game
    --    fingerID:           0-9, used to identify long bars.
    --    actionType:         1: touch down and up
    --                        2: touch down and up with flick
    --                        3: touch down (long bar)
    --                        4: node (long bar)
    --                        5: touch up (long bar)
    --                        6: touch up with flick (long bar)
    -- ]]
    for line in io.lines(file) do
        for str in string.gmatch(line, "[^%s,%[%]]+") do
            actions[#actions + 1] = tonumber(str)
        end
    end
    return actions
end

--[[ ********** #MARK basic utils ********** ]]

function move_to(x1, y1, x2, y2, dur, start_released, end_released)
    if start_released == 0 then touchDown(x1, y1) end
    usleep(dur * 1000000) -- in microseconds
    move_to(x2, y2)
    if end_released == 1 then touchUp(x2, y2) end
end

function rand_loc(btn)
    local function centered_loc(xx1, xx2)
        return (xx1 + xx2) / 2 + (xx1 - xx2) / 2 * (math.random() * 0.9 - 0.45)
    end

    local x1, y1, x2, y2 = btns[btn][1], btns[btn][2], btns[btn][3], btns[btn][4]
    return centered_loc(x1, x2), centered_loc(y1, y2)
end

-- simulates button press on the UI
function btn_press(btn, without_delay)

    local function rand_time_in_us()
        return (1 + math.random() * 5) * 0.5 * 1000000
    end

    local x, y = rand_loc(btn)
    touchDown(0, x, y)

    local time_sep = rand_time_in_us() / sampling_period

    while time_sep > 1 do
        usleep(sampling_period * 1000000)
        touchMove(0, x, y)
        time_sep = time_sep - 1
    end
    touchMove(0, x, y)
    touchUp(0, x, y)

    if not without_delay then usleep(2000000) end
end


--[[ ********** #MARK song playing ********** ]]

function prepare_song(file)
    local actions = {}
    for line in io.lines(file) do
        for str in string.gmatch(line, "[^%s,%[%]]+") do
            actions[#actions + 1] = tonumber(str)
        end
    end
    return actions
end

function play(actions)
    -- get time somehow & manage
    local start_time = socket.gettime()
    for i = 1, #actions, 5 do

        while socket.gettime() < start_time + actions[i] do usleep(500) end
        if actions[i + 4] == 0 then
            touchDown(actions[i + 1], actions[i + 2], actions[i + 3])
        elseif actions[i + 4] == 1 then
            touchMove(actions[i + 1], actions[i + 2], actions[i + 3])
        else
            touchUp(actions[i + 1], actions[i + 2], actions[i + 3])
        end
    end
end


--[[ ********** #MARK image recongition ********** ]]

-- return whether the sceen is the sceen we want
-- todo: allow some error: as long as 80% pixels are within 5% error it is considered as match
function check_sceen_match(sceen, wait, press) while 1 do
    local actual_colors = getColors(key_pixels[sceen])
    local wanted_colors = key_pixels_color[sceen]
    local is_match = 1


    for i = 1, #wanted_colors do
        if not (actual_colors[i] == wanted_colors[i]) then
            is_match = nil
            break
        end
    end


    --    for k,v in pairs(wanted_colors) do
    --        log = log .. ' ' .. v
    --    end
    if is_match then
        if press then btn_press(sceen) end -- press button after match
        return is_match
    elseif not wait then
        return is_match
    end
    usleep(1000)
end
end



-- recognize which album it is. Return the song name.
function recogize_album()
    if is_multimode then end
    return
end

function dectect_difficulty()
end

-- return when ready to play
function wait_until_album_disappear()
    check_sceen_match('black_background', 'wait')
    while 1 do
        if not check_sceen_match('black_background') then
            break
        end
        usleep(1000)
    end
end

-- return when ready to play
function wait_until_other_players_rdy() while 1 do
    if 1 then
        break
    end
    usleep(500)
end
end



--[[ ********** #MARK main ********** ]]
linux_main()
w, h = getScreenResolution()

device_type = init_device_type()
sampling_period = init_sampling_period()

btns = init_btns()
key_pixels, key_pixels_color = init_key_pixels()

math. randomseed(os. time())

is_random_song, is_multi_mode, remaining_loop = nil, nil, 1;
lv = 10;


-- TODO (low) prompt for instruction cycle

-- TODO adjust delay
--    if check_sceen_match('delay') then
--    end

-- autoplay cycle
while remaining_loop > 0 do

local function claim_reward()
end


remaining_loop = remaining_loop - 1

local song_name = 'yes_bang_dream'
local intepreted_score_path = intepreted_score_dir_path.. song_name.. 'expert'.. '.json'
local actions = init_actions_from_intepreted_score(intepreted_score_path)
toast('ready')

--    check_sceen_match('live', 'wait', 'press')
--
--    if is_multi_mode then
--    else
--        check_sceen_match('song_choosing', 'wait')
--        btn_press('confirm_song')
--        check_sceen_match('live_start', 'wait', 'press')
wait_until_album_disappear()
usleep(3000000)
play(actions)
--    end
end
