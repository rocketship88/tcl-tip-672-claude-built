proc live {} { set f /tmp/live.[pid]; memory active $f; set n [llength [split [string trim [exec cat $f]] \n]]; file delete $f; return $n }
set x 5
proc wa {} {global x; list $((1+2)) $(($x*2)) "q$((3))r" $(([expr {1+1}]))}
proc wc {} {global x; list [expr {1+2}] [expr {$x*2}] "q[expr {3}]r" [expr {[expr {1+1}]}]}
foreach n {wa wc} {
  for {set i 0} {$i < 500} {incr i} { $n }
  set prev [live]
  for {set r 0} {$r < 4} {incr r} {
    for {set i 0} {$i < 20000} {incr i} { $n }
    set l [live]; puts "$n round $r: growth [expr {$l-$prev}]"; set prev $l
  }
}
