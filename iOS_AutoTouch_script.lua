function move_to(x1, y1, x2, y2, dur, start_released, end_released)
    if start_released == 0 then touchDown(x1, y1) end
    usleep(dur * 1000000)  -- in microseconds
    move_to(x2, y2)
    if end_released == 1 then touchUp(x2, y2) end
end

function auto_play(actions)
    -- get time somehow
    for k, v in pairs(actions) do

    end
end

lines = {}
actions = {}
file = 'build/128_ichiyamonogatari_expert.txt-timed_actions.json'
for line in io.lines(file) do
    lines[#lines + 1] = line
end

for i = 1, #lines do
    for str in string.gmatch(lines[i], "[^%s,%[%]]+") do
        actions[#actions+1] = tonumber(str)
    end
end


for k, v in pairs(actions) do print(v) end

