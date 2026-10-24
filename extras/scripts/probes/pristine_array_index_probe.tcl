puts [info patchlevel]
set ::tcl_interactive 0
array set {} [list a 1 1+2 three { 1+2} sp (1+2) p1 ( p2 {} e]
set cases [list {$((1+2))} {$( (1+2))} {$(  (1+2))} {$((1+2)*3)} {$(1+2)} {$( 1+2)} {$()} {$(} {$((} {$(()} {$(())} {$(a)} {$((a))} {$( (a))} "\$(\n(a))" {$(a b)} {$($x)} {$([set y])} {$(\()} {$(\))} {$({a})} {$("a")}]
set x k; set y z
foreach c $cases {
  puts -nonewline [format "%-14s => " [string map {\n \\n} $c]]
  if {[catch {subst $c} r]} {puts "ERR [string map {\n { | }} $r]"} else {puts "'$r'"}
}
puts "--- as script words"
foreach c $cases {
  puts -nonewline [format "%-14s => " [string map {\n \\n} $c]]
  if {[catch {eval "set v \"$c\""} r]} {puts "ERR [string map {\n { | }} $r]"} else {puts "'$r'"}
}
