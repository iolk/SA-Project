set d 3000
loop
wait 100
read tmp
if($tmp != "")
	set d $tmp
end
areadsensor s
battery x
sadd 1 x
send $x 4 
delay $d