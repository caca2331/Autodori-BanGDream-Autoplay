sampling_period = 1 / 60 -- sampling period of screen, used to calucuate # of move event generated. In seconds.


function move_to(x1, y1, x2, y2, dur, start_released, end_released)
    if start_released == 0 then touchDown(x1, y1) end
    usleep(dur * 1000000) -- in microseconds
    move_to(x2, y2)
    if end_released == 1 then touchUp(x2, y2) end
end

function print_actions(actions)
    for i = 1, #actions, 5 do
        print(actions[i], actions[i + 1], actions[i + 2], actions[i + 3], actions[i + 4])
    end
end

function wait_cover_disappear()
    while 1 do

        if 1 then
            break
        end
        usleep(500)
    end
end

function wait_till_all_rdy()
    while 1 do

        if 1 then
            break
        end
        usleep(500)
    end
end

function play(actions)
    -- get time somehow & manage
    local start_time = 0 -- TODO
    for i = 1, #actions, 5 do
        while time --[[ TODO ]] < start_time + actions[i] do usleep(500) end
        if actions[i + 4] == 0 then
            touchDown(actions[i + 1], actions[i + 2], actions[i + 3])
        elseif actions[i + 4] == 1 then
            touchMove(actions[i + 1], actions[i + 2], actions[i + 3])
        else
            touchUp(actions[i + 1], actions[i + 2], actions[i + 3])
        end
    end
end

function prepare_song(file)
    local actions = {}
    for line in io.lines(file) do
        for str in string.gmatch(line, "[^%s,%[%]]+") do
            actions[#actions + 1] = tonumber(str)
        end
    end
    return actions
end

-- init locations for buttons in the UI
function init_btns()
    if 1 --[[ TODO ratio of ipad]] then
        local iPad_pixels = {
            live = { 1, 2, 3, 4 },
            easy = { 1, 1, 5, 5 }
        }
        local w_r, h_r = -1, -1 --TODO

        for k, v in pairs(iPad_pixels) do
            iPad_pixels[k] = { v[1] * w_r, v[2] * h_r, v[3] * w_r, v[4] * h_r }
        end
        return iPad_pixels
    end
end

-- init locations and initeger_color of pixels to check
function init_key_pixels()
    if 1 --[[ TODO ratio of ipad]] then
        local iPad_pixels = {
            live = {
                { 1, 2 }, { 3, 4 }
            }
        }
        local iPad_pixels_color = {
            live = { 1, 2 }
        }
        local w_r, h_r = -1, -1 --TODO
        for k, v in pairs(iPad_pixels) do
            for kk, vv in pairs(v) do
                v[kk] = { vv[1] * w_r, vv[2] * h_r }
                iPad_pixels[k] = v
            end
        end
        return iPad_pixels, iPad_pixels_color
    end
end

-- simulates button press on the UI
function btn_press(btn)
    local function centered_loc(xx1, xx2)
        return (xx1 + xx2) / 2 + (xx1 - xx2) / 2 * (math.random() * 0.9 - 0.45)
    end

    local function rand_time_in_us()
        return (1 + math.random() * 5) * 0.5 * 1000000
    end

    local x1, y1, x2, y2 = btns[btn][1], btns[btn][2], btns[btn][3], btns[btn][4]
    local x, y = centered_loc(x1, x2), centered_loc(y1, y2)
    touchDown(0, x, y)

    local time_sep = rand_time_in_us() / sampling_period

    while time_sep > 1 do
        usleep(sampling_period * 1000000)
        touchMove(0, x, y)
        time_sep = time_sep - 1
    end
    touchMove(0, x, y)
    touchUp(0, x, y)
end

-- return whether the sceen is the sceen we want
function check_sceen_match(sceen, wait) while 1 do
    local actual_colors = getColors(key_pixels[sceen])
    local wanted_colors = key_pixels_color[sceen]
    local is_match = 1

    for i = 1, #wanted_coloes do
        if actual_colors[i] == wanted_colors[i] then
            is_match = 0
            break
        end
    end

    if is_match or not wait then return is_match end
    usleep(10000)
end end


w, h = getScreenResolution()
btns = init_btns()
key_pixels, key_pixels_color = init_key_pixels()

is_random_song, is_multi_mode, remaining_loop = 0, 0, 1;

math.randomseed(os.time())

file = 'build/test.json'
actions = prepare_song(file)

-- TODO low prompt for instruction cycle

-- autoplay cycle
while (remaining_loop > 0.1) do
    remaining_loop = remaining_loop - 1
    check_sceen_match('live')
2
    btn_press('live')
end



