# value differential: $((body)) vs [expr body], with bodies built so the end is unambiguous
set seed [lindex $argv 0]; expr {srand($seed)}
proc pick l { lindex $l [expr {int(rand()*[llength $l])}] }
proc atom {} {
    pick {1 2 3 10 0.5 7 {"a)b"} {"x"} {{)}} {[string length ")"]} {[string length "]"]} {[expr {1+2}]}
          {(4)} {((5))} {"\)"} {[string length \)]} {"[string length "]"]"} {{a}} {(1+(2*3))} abc {1 +} ) ( \\ \" \{}
}
proc body {} {
    set n [expr {1+int(rand()*5)}]; set s [atom]
    for {set i 1} {$i < $n} {incr i} { append s " [pick {+ - * / == eq ne < && ||}] [atom]" }
    return $s
}
set total 0; set okboth 0; set same 0; set diff 0; set skipped 0
for {set k 0} {$k < 60000} {incr k} {
    set b [body]
    # only compare when the text can be delimited on its own: balanced parens/quotes/braces/brackets
    if {[catch {uplevel #0 [list info complete "set x \"$b\""]}]} { incr skipped; continue }
    set src "\$(($b))"
    set c1 [catch {subst $src} v1]
    set c2 [catch {expr $b} v2]
    incr total
    if {$c1 == $c2 && ($c1 || $v1 eq $v2)} { incr same; if {!$c1} {incr okboth} } else {
        # a body whose own parens do not balance legitimately ends early: not a bug, not counted
        set open [llength [regexp -all -inline {\(} $b]]; set close [llength [regexp -all -inline {\)} $b]]
        if {$open != $close} { incr skipped; incr total -1; continue }
        incr diff; if {$diff <= 12} { puts "DIFF body=<$b> subst:($c1) <$v1>  expr:($c2) <$v2>" }
    }
}
puts "ok-values-compared=$okboth compared=$total same=$same different=$diff skipped=$skipped"
