# many continuation-line scenarios: line of an error raised inside $((...)) vs inside [expr {(...)}]
set scen {
 {set v "a\
b $(([error boom]))"}
 {set v "a\
\
b $(([error boom]))"}
 {set v "a\
b $((1 +
   [error boom]))"}
 {set v "x\
y\
z $((1)) $(([error boom]))"}
 {set v "a\
b $(([list a\
b] + [error boom]))"}
 {puts [list "p\
q $((1+1))" [error boom]]}
 {set v "a\
b $((1)) c\
d $(([error boom]))"}
}
set i 0
foreach s $scen {
    incr i
    set ref [string map [list {$((} {[expr {(} {))} {)}]}] $s]
    # build ref from s: replace $(( ... )) with [expr {( ... )}]
    set ref [regsub -all {\$\(\((.*?)\)\)} $s {[expr {(\1)}]}]
    proc A {} "catch {$s} m o; dict get \$o -errorline"
    proc B {} "catch {$ref} m o; dict get \$o -errorline"
    puts "scenario $i: new=[A] ref=[B]"
}
