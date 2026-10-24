# usage: TCL_LIBRARY=<tcl>/library tcltest gen.tcl > dataN.json   (run once per build)
# Collects real parser, bytecode and result data for each scenario, for both $(expr) and the [expr {expr}] it stands for.
proc js {s} { string map [list \\ \\\\ \" \\\" \n \\n \r {} \t \\t] $s }
set scen {
 {basic     {set v $((1+2*3))}}
 {missing   {set v $((1+2)*3)}}
 {nested    {set v "a$((1+(2*3)))z"}}
 {braces    {set v $(({a )} eq {a )}))}}
 {unterm    {set v $((1+2)}}
 {runtime   {$(([return -code error boom]))}}
 {single    {set v $(1+2)}}
 {typo      {set v $((  1+2)*3  ))}}
 {var       {set v $(($x*2))}}
}
set out {}
set x 5
foreach s $scen {
  lassign $s name src
  if {[catch {testparser $src 0} tok]} { set tok "ERROR: $tok" }
  if {$name eq "runtime"} { set t $src; set r [catch {subst $t} res] } else { set r [catch {eval $src} res] }
  if {[catch {tcl::unsupported::disassemble script $src} dis]} { set dis "ERROR: $dis" }
  # the reference form [expr {body}]: body is the text of the token after "exprsubst"
  set body ""; set tokText ""
  if {![string match ERROR* $tok]} {
    set it $tok
    for {set k 3} {$k+4 < [llength $it]} {incr k 3} {
      if {[lindex $it $k] eq "exprsubst"} { set tokText [lindex $it $k+1]; set body [lindex $it $k+4]; break }
    }
  }
  set refSrc ""; set refTok ""; set refDis ""; set refRc ""; set refRes ""; set tree ""
  if {$tokText ne ""} {
    set di [string first $tokText $src]
    set refSrc [string replace $src $di [expr {$di+[string length $tokText]-1}] "\[expr {$body}\]"]
    if {[catch {testparser $refSrc 0} refTok]} { set refTok "ERROR: $refTok" }
    if {$name eq "runtime"} { set t $refSrc; set refRc [catch {subst $t} refRes] } else { set refRc [catch {eval $refSrc} refRes] }
    if {[catch {tcl::unsupported::disassemble script $refSrc} refDis]} { set refDis "ERROR: $refDis" }
    if {[catch {testexprparser $body 0} tree]} { set tree "ERROR: $tree" }
  }
  lappend out "\"$name\":{\"src\":\"[js $src]\",\"tokens\":\"[js $tok]\",\"rc\":$r,\"res\":\"[js $res]\",\"dis\":\"[js $dis]\",\"body\":\"[js $body]\",\"refSrc\":\"[js $refSrc]\",\"refTok\":\"[js $refTok]\",\"refRc\":\"[js $refRc]\",\"refRes\":\"[js $refRes]\",\"refDis\":\"[js $refDis]\",\"tree\":\"[js $tree]\"}"
}

# subst options: the same text with each option, real results
set x 5
foreach {key opt} {d {} ne -noexpressions e -expressions nc -nocommands nv -novariables nb -nobackslashes} {
  set cmd [string map {"subst  " "subst "} "subst $opt \{\$((1+2)) \$x \[set y 7\]\}"]
  set r [catch {eval $cmd} res]
  lappend out "\"subst_$key\":{\"src\":\"[js $cmd]\",\"rc\":$r,\"res\":\"[js $res]\"}"
}
puts "{[join $out ,]}"
