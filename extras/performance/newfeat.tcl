# New-feature cost: expression substitution vs the [expr {...}] it is equivalent to
set N 10
set sP {}; set sE {}
for {set k 0} {$k < 200} {incr k} {
  append sP "set v$k \$((\$x*$k+\$y)); "
  append sE "set v$k \[expr {(\$x*$k+\$y)}\]; "
}
set x 3; set y 4
for {set i 0} {$i < $N} {incr i} {
    set mode [lindex $argv 0]
    switch $mode {
      subst_new  { eval [string cat $sP $i] }
      subst_old  { eval [string cat $sE $i] }
      comp_new   { proc q$i {} "$sP #$i"; q$i; rename q$i {} }
      comp_old   { proc q$i {} "$sE #$i"; q$i; rename q$i {} }
    }
}
