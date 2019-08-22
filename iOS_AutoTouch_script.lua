--socket = require("socket")


--- [[ ********** #MARK global variables ********** ]]

-- paths
score_dir_path = "/var/mobile/Library/AutoTouch/Scripts/Autodori/score"
intepreted_score_dir_path = "/var/mobile/Library/AutoTouch/Scripts/Autodori/interpreted"
playable_dir_path = "/var/mobile/Library/AutoTouch/Scripts/Autodori/playable"
-- config
is_random_miss = 1
is_random_time = 1
is_random_song = nil
is_multi_mode = nil
remaining_loop = nil
-- normal good player(fc lv25 songs) will be 10,
-- 20 will be very good player,
-- 25 will be top 10 player,
-- 30+ will be suspicious (risky!)
lv = nil
difficulty = nil
-- constants
F_DUR = 0.08 -- expected duration of flick
STICK_DUR = 0.05 -- expected duration of a touch on the the screen
SLIDE_STICK_DUR = 0.08 -- min time for a finger to stay between two notes within a slide
P_RANGE = 0.04 -- boundary that a touch is graded as perfect (in both directions), in seconds
IN_AIR_DUR = 0.08 -- min time for a finger to stay in air between two touches

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
key_pixels_color = nil
song_info = nil
-- touch actions to be performed
actions = nil


--- [[ ********** #MARK basic utils ********** ]]
function move_to(x1, y1, x2, y2, dur, start_released, end_released)
    if start_released == 0 then touchDown(x1, y1) end
    usleep(dur * 1000000) -- in microseconds
    move_to(x2, y2)
    if end_released == 1 then touchUp(x2, y2) end
end

function rand_loc(btn, y1, x2, y2)
    local function centered_loc(xx1, xx2)
        return (xx1 + xx2) / 2 + (xx1 - xx2) / 2 * (math.random() * 0.9 - 0.45)
    end

    if y1 then return centered_loc(btn, x2), centered_loc(y1, y2)
    else print(btn)--, btns[btn][1], btns[btn][3], btns[btn][2], btns[btn][4] )
        return centered_loc(btns[btn][1], btns[btn][3]), centered_loc(btns[btn][2], btns[btn][4])
    end
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


--- [[ ********** #MARK initialization ********** ]]

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
            { 215, 1200, 469, 1270 },
            { 470, 1200, 724, 1270 },
            { 726, 1200, 980, 1270 },
            { 982, 1200, 1236, 1270 },
            { 1237, 1200, 1491, 1270 },
            { 1492, 1200, 1746, 1270 },
            { 1748, 1200, 2006, 1270 },
            { 215, 1100, 469, 1170 },
            { 470, 1100, 724, 1170 },
            { 726, 1100, 980, 1170 },
            { 982, 1100, 1236, 1170 },
            { 1237, 1100, 1491, 1170 },
            { 1492, 1100, 1746, 1170 },
            { 1748, 1100, 2006, 1170 },
            live = { 1, 2, 3, 4 },
            easy = { 1, 1, 5, 5 }
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

-- generate a random playable score
function init_actions_from_intepreted_score(file)

    local function gen_action_info(interpreted, old_finger, i)

        -- (40% 0-0.3 21% 0.3-0.5 19% 0.5-0.72 18% 0.72-0.95 2% 0.95-1) * p_perfect
        -- (50% 1-1.4 32% 1.4-1.7 10% 1.7-2.0 5% 2.0-2.5 3% 2.5-3.0) * p_great
        local real_diff = math.max(0, difficulty - 20)
        local p_perfect = .85 + .15 * (1 - .8 ^ lv * 1.2 ^ real_diff)
        local great_miss_ratio = lv / 1.2 ^ real_diff

        local function rand_time_offset()
            local is_perfect = math.random() < p_perfect
            local is_missed = is_random_miss and (not is_perfect) and (math.random() < 1 / (great_miss_ratio + 1))

            if is_missed then return nil end

            if is_random_time then
                local multiplier, score
                if math.random() > 0.5 then multiplier = P_RANGE else multiplier = -P_RANGE end

                local dice = math.random()
                if is_perfect then
                    if dice < 0.4 then score = 0.3 * math.random()
                    elseif dice < 0.61 then score = 0.3 + 0.2 * math.random()
                    elseif dice < 0.8 then score = 0.5 + 0.22 * math.random()
                    elseif dice < 0.98 then score = 0.72 + 0.23 * math.random()
                    else score = 0.95 + 0.05 * math.random()
                    end
                else
                    if dice < 0.5 then score = 1 + 0.4 * math.random()
                    elseif dice < 0.82 then score = 1.4 + 0.3 * math.random()
                    elseif dice < 0.92 then score = 1.7 + 0.3 * math.random()
                    elseif dice < 0.97 then score = 2 + 0.5 * math.random()
                    else score = 2.5 + 0.5 * math.random()
                    end
                end
                return multiplier * score

            else return 0
            end
        end

        local function gen_action_duration(action_type)
            if action_type == 1 then
                return (0.5 + math.random()) * STICK_DUR
            elseif action_type == 2 then
                return (0.5 + math.random()) * F_DUR
            end
        end

        local function gen_touch_loc(player_loc, is_flick)
            print('player_loc',player_loc)
            if is_flick then return rand_loc(player_loc)
            else return rand_loc(player_loc + 7)
            end
        end


        local action_type = interpreted[i + 3]
        local f_id = interpreted[i + 2]
        local last_action = old_finger[f_id]
        local time_offest = rand_time_offset()

        local start_time, duration, end_time
        local x1, y1, x2, y2
        local s_attached, e_attached

        if action_type < 3 then --- click
            if not time_offest then return nil end -- intentially miss
            start_time = interpreted[i] + time_offest
            duration = gen_action_duration(action_type)
            end_time = start_time + duration
            x1, y1 = gen_touch_loc(interpreted[i + 1], action_type == 2)
            x2, y2 = rand_loc(x1 - 5, y1 - 5, x1 + 5, y1 + 5)
            s_attached, e_attached = false, false

        elseif action_type == 5 then return nil --- long bar end (ignored)

        else --- long bar

            -- intentionally miss long bar
            if not time_offest then
                if not last_action then return nil -- create new action, but intentionally miss
                else -- finishing last action: end with nil
                    last_action[9] = false
                    return nil
                end
            end

            if last_action then -- appending to previous action
                start_time = last_action[3]
                x1, y1 = last_action[6], last_action[7]
                s_attached = true
            else -- create new action
                start_time = interpreted[i] + time_offest
                x1, y1 = gen_touch_loc(interpreted[i + 1])
                s_attached = false
            end

            if action_type == 6 then -- flick end
                duration = gen_action_duration(2)
                end_time = start_time + duration
                x2, y2 = gen_touch_loc(interpreted[i + 1], true)
                e_attached = false
            else -- get next non-end-action
                local next_acion = i
                while interpreted[next_acion + 2] ~= f_id do next_acion = next_acion + 4 end
                end_time = interpreted[i] + time_offest
                if start_time + SLIDE_STICK_DUR > end_time then end_time = start_time + SLIDE_STICK_DUR end
                duration = end_time - start_time
                x2, y2 = gen_touch_loc(interpreted[i + 1])
                if interpreted[next_acion + 3] == 5 then e_attached = false
                else e_attached = true
                end
            end
        end

        local info = { start_time, duration, end_time, x1, y1, x2, y2, s_attached, e_attached, f_id }
        info[11] = (info[6] - info[4]) / info[2] * sampling_period -- dx
        info[12] = (info[7] - info[5]) / info[2] * sampling_period -- dy
        info[-2] = last_action
        if e_attached then old_finger[f_id] = info
        else old_finger[f_id] = nil
        end
        return info
    end

    local function insert_to_actions(actions, action_info, insertion_type)
        table.insert(actions, action_info[1])
        table.insert(actions, action_info[-1])
        if insertion_type == 2 then
            table.insert(actions, action_info[4])
            table.insert(actions, action_info[5])
        else table.insert(actions, action_info[6])
            table.insert(actions, action_info[7])
        end
        table.insert(actions, insertion_type)
        action_info[1] = action_info[1] + sampling_period
        action_info[2] = action_info[2] - sampling_period
        action_info[4] = action_info[4] + action_info[11]
        action_info[5] = action_info[5] + action_info[12]
    end

    --[[
    -- [[ timeOfAction, locationOfAction, fingerID, actionType ], ...]
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
    local interpreted = {}
    local temp_stack = {} -- allow max of four fingers at the same time
    local actions = {}
    local old_finger = {}
    local new_finger = {}
    local curr_time = 0
    for line in io.lines(file) do
        for str in string.gmatch(line, "[^%s,%[%]]+") do
            table.insert(interpreted, tonumber(str))
        end
    end
    local i = 1

    -- go through each interpreted_score
    while 1 do
        if (i > #interpreted) and (#temp_stack == 0) then break end
        while (interpreted[i] + 3 * P_RANGE) < curr_time do
            table.insert(temp_stack, gen_action_info(interpreted, old_finger, i))
            i = i + 4
        end

        while 1 do
            --- find earliest action
            local earliest_idx = 1
            for ii = 2, #temp_stack do
                if temp_stack[ii][1] < temp_stack[earliest_idx][1] then earliest_idx = ii end
            end
            if (#temp_stack == 0) or (temp_stack[earliest_idx][1] > curr_time) then break end

            local temp_action = temp_stack[earliest_idx]

            --- assign new finger and add touch_down action
            if not temp_action[-1] then
                if temp_action[-2] then -- if the action is continued from previous one, use previous one's new finger
                    temp_action[-1] = temp_action[-2][-1]
                    new_finger[temp_action[-1]] = true

                else
                    for ii = 1, 4 do
                        if not (new_finger[ii]) then
                            temp_action[-1] = ii
                            new_finger[ii] = true
                            break
                        end
                        if not temp_action[-1] then
                            if is_linux_main then print('more than four fingers at same time!')
                            else toast('more than four fingers at same time!')
                            end
                        end
                    end
                end
            end

            --- add to actions

            if temp_action[8] then
                insert_to_actions(actions, temp_action, 1) -- start with finger attached, thus move
            else
                insert_to_actions(actions, temp_action, 0) -- start with finger attached, thus touch down
                temp_action[8] = false
            end
            if temp_action[2] < 0.001 then -- finger up; stop tracking
                insert_to_actions(actions, temp_action, 2)
                new_finger[temp_action[-1]] = nil
                table.remove(temp_stack, earliest_idx)
            end
        end

        curr_time = curr_time + sampling_period
    end
    return actions
end


--- [[ ********** #MARK song playing ********** ]]
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

    --[ starttime, finger_id, x, y, finger_attaching/moving/leaving(0/1/2)]
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


--- [[ ********** #MARK image recongition ********** ]]

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



--- [[ ********** #MARK debugging ********** ]]
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

-- debug score generation
function linux_main()
    is_linux_main = true
    w, h = 2224, 1668

    device_type = init_device_type()
    sampling_period = init_sampling_period()

    btns = init_btns()
    key_pixels, key_pixels_color = init_key_pixels()

    math.randomseed(os.time())

    is_random_song, is_multi_mode, remaining_loop = nil, nil, 1;
    lv, difficulty = 10, 25

    actions = init_actions_from_intepreted_score('interpreted/yes_bang_dream_expert_interpreted.json')
    print_actions()
    os.exit(0)
end



--[[ ********** #MARK main ********** ]]

linux_main()
w, h = getScreenResolution()

device_type = init_device_type()
sampling_period = init_sampling_period()

btns = init_btns()
key_pixels, key_pixels_color = init_key_pixels()

math.randomseed(os.time())

is_random_song, is_multi_mode, remaining_loop = nil, nil, 1
lv = 10


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
    local intepreted_score_path = intepreted_score_dir_path .. song_name .. 'expert' .. '.json'
    local playable = '/var/mobile/Library/AutoTouch/Scripts/Autodori/playable/yes_bang_dream_expert_playable.json'
    --    local actions = init_actions_from_intepreted_score(intepreted_score_path)
    local actions = prepare_song(playable)
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
