proc live {} { set f /tmp/live.[pid]; memory active $f; set n [llength [split [string trim [exec cat $f]] \n]]; file delete $f; return $n }
set x 5
proc fp {} { set v 3; return [list $((1+$v)) "a$(([string length abc]*2))b" ${v}] }
set cases {
 a {list $((1+2)) $(($x*2)) "q$((3))r" $(([expr {1+1}]))}
 b {list [subst {$((1+$x))}] [subst -nocommands {$((1+$x))}] [subst -noexpressions {$((1+2))}]}
 c {list [catch {subst {$((1+}} m] [catch {subst {$((1+2)}} m] [catch {subst {$((1/0))}} m] [catch {subst {$((}} m]}
 d {list [catch {eval {set y $((1+}} m] [catch {eval {set y $((1+2)}} m] [catch {eval {set y $((1/0))}} m]}
 e {list [fp] [eval {set z $((1+2))}] [uplevel #0 {set z2 "$((4*4))"}]}
 f {list [catch {expr {$((1+2))}} m] [catch {expr {1 + $(($x))}} m]}
 g {list [catch {set q $((1+[error boom]))} m] [catch {set q $((1+[return r]))} m] [catch {set q $((1+[break]))} m]}
 h {list [catch {array set aa {}; set aa($((1+1))) 5} m]}
 ctl1 {list [catch {eval {set y [expr {1+}}} m]}
 ctl2 {list [catch {subst {[expr {1/0}]}} m] [catch {eval {set y [expr 1/0]}} m]}
}
foreach {name body} $cases {
    proc w$name {} "global x; $body"
    for {set i 0} {$i < 500} {incr i} { w$name }
    set b [live]
    for {set i 0} {$i < 20000} {incr i} { w$name }
    puts "$name: growth over 20000 = [expr {[live]-$b}]"
}
