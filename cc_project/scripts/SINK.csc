set topic "sensor_power"
set first_sep ","
set second_sep "::"
set n_sensor 4
vec powers $n_sensor
vec updated $n_sensor
set i 1
while(i<n_sensor)
    vset 0 updated i
    vset 0 powers i
    inc i
end
loop
wait
read tmp
if(tmp != "")
    nth from 0 tmp
    nth power 1 tmp
    vset power powers from
    vset 1 updated from
    set all_updated 1
    set i 1
    while(i<n_sensor)
        vget tmp updated i
        if(tmp == 0)
            set all_updated 0
        end
        inc i
    end
    if(all_updated == 1)
        set power_message \
        set i 1
        while(i<n_sensor)
            vget tmp powers i
            set comparator $n_sensor
            dec comparator
            if(i != comparator)
                function power_message concatenate 5,$power_message,$i,$first_sep,$tmp,$second_sep
            else
                function power_message concatenate 4,$power_message,$i,$first_sep,$tmp
            end
            inc i
        end
        print $power_message
        function y kafkaProduce $topic,$power_message
    end
end