set n [lindex $argv 0]
set body [string repeat "1+" $n]1
set s "\$(($body))"
set r [subst $s]
catch {subst [string range $s 0 end-1]}      ;# unterminated
set d [string repeat "(" $n][string repeat ")" $n]
catch {subst "\$(($d))"}
puts $r
