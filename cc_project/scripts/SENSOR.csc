set normal_delay 0
set critical_delay 0
set mode_threshold 0
atget id id
set controller $id/10
int controller $controller
set first_config 0
loop
if (first_config == 0)
	wait
	set first_config 1
else
	wait 100
end
read tmp
if($tmp != "")
	nth normal_delay 0 tmp
	nth critical_delay 1 tmp
	nth mode_threshold 2 tmp
	print $normal_delay $critical_delay $mode_threshold
end
areadsensor v
print $v
set x ""
rdata $v a b x
int counter $x
if (x!=0.0)
	sadd $id x
	send $x $controller
end
if(counter>mode_threshold)
	print "Critical!"
	delay $critical_delay
else
	delay $normal_delay
end
