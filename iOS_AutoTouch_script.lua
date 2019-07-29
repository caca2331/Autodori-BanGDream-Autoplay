sampling_frequency = 2000 -- sampling frequency of screen, used to calucuate # of move event generated. In micro-seconds.

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

function init_play()
end
function play(actions)
    -- get time somehow & manage
    for i = 1, #actions, 5 do
        move_to(actions[i], actions[i + 1], actions[i + 2], actions[i + 3],
            actions[i + 4], actions[i + 5], actions[i + 6], actions[i + 7], actions[i + 8])
    end
end

actions = {}
file = 'build/test.json'
for line in io.lines(file) do
    for str in string.gmatch(line, "[^%s,%[%]]+") do
        actions[#actions + 1] = tonumber(str)
    end
end

print_actions(actions)
