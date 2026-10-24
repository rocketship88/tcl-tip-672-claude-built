proc p1 {} {
    return "a\
b[expr {[dict get [info frame 0] line]}]"
}
proc p2 {} {
    return "a\
b$(([dict get [info frame 0] line]))"
}
proc p3 {} {
    return "a\
b$(([dict get [info frame 0] line]+0))[expr {[dict get [info frame 0] line]}]"
}
proc p4 {} {
    return "a\
b[expr {[dict get [info frame 0] line]}]$(([dict get [info frame 0] line]))"
}
puts "[p1] [p2]"
puts [p3]
puts [p4]
