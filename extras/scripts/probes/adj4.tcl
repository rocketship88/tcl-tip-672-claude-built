set x "a\tb[set y 1]"
puts $x
set x "a\
  b[set y 1]"
puts $x
proc p {} {
 set x "a\
  b[set y 1]"
}
p
