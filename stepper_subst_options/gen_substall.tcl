# usage: tclsh gen_substall.tcl > substallN.json   (run once per build)
# Real results of  subst <options> {$((1+2)) $x [set y 7] \$x}  for all 256 combinations of the 8 options.
proc js {s} { string map [list \\ \\\\ \" \\\" \n \\n \r {} \t \\t] $s }
set names {-backslashes -commands -variables -expressions -nobackslashes -nocommands -novariables -noexpressions}
set body {$((1+2)) $x [set y 7] \$x}
set x 5
set out {}
for {set m 0} {$m < 256} {incr m} {
  set opts {}
  for {set k 0} {$k < 8} {incr k} { if {$m & (1 << $k)} { lappend opts [lindex $names $k] } }
  set r [catch {subst {*}$opts $body} res]
  set head [expr {[llength $opts] ? "subst [join $opts { }] " : "subst "}]
  lappend out "\"$m\":{\"src\":\"[js "$head\{$body\}"]\",\"rc\":$r,\"res\":\"[js $res]\"}"
}
puts "{[join $out ,]}"
