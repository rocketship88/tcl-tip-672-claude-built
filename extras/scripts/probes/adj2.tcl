set x "a\
b[dict get [info frame 0] line]"
set y "a\
b$(([dict get [info frame 0] line]))"
puts "$x $y"
set z "a\
b[expr {[dict get [info frame 0] line]}]"
puts $z
proc q {} {
    set l [info frame 0]
    return $l
}
puts [eval {set w "a\
b[dict get [info frame 0] line]"}]
puts [eval {set w "a\
b$(([dict get [info frame 0] line]))"}]
