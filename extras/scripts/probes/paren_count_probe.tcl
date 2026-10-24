foreach s {{$((1+2)*3)} {$((  1+2)*3  ))} {$((  (1+2)*3  ))} {$((1+2))} {$(1+2)} {$((1+2)*3))}} {
  puts -nonewline "$s  =>  "
  if {[catch {subst $s} r]} {puts "ERR [lindex [split $r \n] 0]"} else {puts "'$r'"}
}
