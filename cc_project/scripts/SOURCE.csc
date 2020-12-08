set consume_topic "adaptations"
loop
function y kafkaConsume $consume_topic
println $y
delay 1000