puts [info patchlevel]
set ::tcl_interactive 0
catch {set x "a$(1+2)b"} r; puts "1: $r"
set "(" zero; set ()  empty
catch {set y $(} r; puts "2: $r"
catch {set y $()} r; puts "3: $r"
set a(1) one
catch {set z $a(1)} r; puts "4: $r"
puts [list [catch {subst {$(1+2)}} r] $r]
