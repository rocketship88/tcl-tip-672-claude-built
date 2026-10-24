# runtime of an already compiled loop (should be identical bytecode)
proc a {n} {set s 0; for {set i 0} {$i<$n} {incr i} {set s [expr {($i*2+1)}]}; set s}
proc b {n} {set s 0; for {set i 0} {$i<$n} {incr i} {set s $(($i*2+1))}; set s}
foreach p {a b} { puts "$p [lindex [time {$p 200000} 3] 0]" }
