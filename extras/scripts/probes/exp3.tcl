set scen {
 {set v "a\
b $(([dict get [info frame 0] line]))"}
 {set v "a\
\
b $(([dict get [info frame 0] line]))"}
 {set v "x\
y\
z $((1)) $(([dict get [info frame 0] line]))"}
 {set v "a\
b $((1 +
   [dict get [info frame 0] line]))"}
 {set v "a\
b $((1)) c\
d $(([dict get [info frame 0] line]))"}
 {set v "$(([dict get [info frame 0] line]))"}
}
set i 0
foreach s $scen {
    incr i
    set ref [regsub -all {\$\(\((.*?)\)\)(?=\"|$)} $s {[expr {(\1)}]}]
    set ref [string map {{$((1))} {[expr {(1)}]}} $ref]
    proc A {} "$s\nreturn \$v"
    proc B {} "$ref\nreturn \$v"
    puts "scenario $i: new=[A] ref=[B]"
}
