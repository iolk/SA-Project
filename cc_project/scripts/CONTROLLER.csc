atget id id
set s1_id id*10+1
set s2_id id*10+2
set sink 1
set count 0
set topic "sensors_data"
loop
set div $count%20
int div $div
print $div
if(div == 0)
    function y getSensorsConfig $id
    rdata y s1 s2
    send $s1 s1_id
    send $s2 s2_id
    set count 1
end
wait
read tmp
if(tmp != "")
    nth from 0 tmp
    nth sensor_data 1 tmp
    print $from $sensor_data
    function y logSensorData $from,$sensor_data
    function y kafkaProduce $topic,$tmp
    set count $count+1
end