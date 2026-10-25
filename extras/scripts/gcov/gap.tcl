proc t {l s} { if {[catch {uplevel #0 $s} r]} {puts "$l: ERR [string range $r 0 70]"} else {puts "$l: $r"} }
t strayBracket   {subst {$((1 ] 2))}}
t strayBracket2  {subst {$((1)] )}}
t completeBad    {info complete {puts $((1+2)x)}}
t completeOpen   {info complete {puts $((1+2)}}
t completeOpen2  {info complete {puts $((1+2}}
t completeOk     {info complete {puts $((1+2))}}
t parseNoInterp  {info complete "set a \$((1+2)\n"}
