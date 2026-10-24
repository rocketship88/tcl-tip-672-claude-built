# leak growth test: run each construct many times, compare live blocks before/after
proc live {} { set f /tmp/live.[pid]; memory active $f; set n [llength [split [string trim [exec cat $f]] \n]]; file delete $f; return $n }
set x 5
proc fp {} { set v 3; return [list $((1+$v)) "a$(([string length abc]*2))b" ${v}] }
proc work {} {
    global x
    set r {}
    lappend r $((1+2)) $(($x*2)) "q$((3))r" $(([expr {1+1}]))
    lappend r [subst {$((1+$x))}] [subst -nocommands {$((1+$x))}] [subst -noexpressions {$((1+2))}]
    lappend r [catch {subst {$((1+}} m] [catch {subst {$((1+2)}} m] [catch {subst {$((1/0))}} m] [catch {subst {$((}} m]
    lappend r [catch {eval {set y $((1+}} m] [catch {eval {set y $((1+2)}} m] [catch {eval {set y $((1/0))}} m]
    lappend r [fp] [eval {set z $((1+2))}] [uplevel #0 {set z2 "$((4*4))"}]
    lappend r [catch {expr {$((1+2))}} m] [catch {expr {1 + $(($x))}} m]
    lappend r [catch {set q $((1+[error boom]))} m] [catch {set q $((1+[return r]))} m] [catch {set q $((1+[break]))} m]
    lappend r [catch {array set aa {}; set aa($((1+1))) 5} m]
    return $r
}
for {set i 0} {$i < 200} {incr i} { work }   ;# warm up caches and literal tables
set before [live]
for {set i 0} {$i < 3000} {incr i} { work }
set after [live]
puts "live blocks before=$before after=$after growth=[expr {$after-$before}]"
for {set i 0} {$i < 3000} {incr i} { work }
set after2 [live]
puts "second 3000: growth=[expr {$after2-$after}]"
for {set i 0} {$i < 12000} {incr i} { work }
puts "next 12000: growth=[expr {[live]-$after2}]"
