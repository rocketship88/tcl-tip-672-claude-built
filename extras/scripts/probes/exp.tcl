puts "testevalex: [llength [info commands testevalex]]  testparser: [llength [info commands testparser]]"
puts "info complete unterminated: [info complete {puts $((1+2)}]  terminated: [info complete {puts $((1+2))}]"
set s {a$((1+1))b}
puts "subst nonliteral: [subst $s]"
puts "testevalex: [testevalex {set v a$((1+1))b}]"
# continuation / line tracking
proc P {} {
    catch {
        set v "a\
b $(([error boom]))"
    } m o
    dict get $o -errorline
}
proc R {} {
    catch {
        set v "a\
b [expr {([error boom])}]"
    } m o
    dict get $o -errorline
}
puts "errorline new=[P] ref=[R]"
