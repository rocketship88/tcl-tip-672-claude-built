# plain Tcl
proc crossPlain {U V} {
    lassign $U x y z
    lassign $V u v w
    list [expr {$y*$w - $v*$z}] [expr {$w*$x - $u*$z}] [expr {$x*$v - $u*$y}]
}

# TIP 672
proc cross672 {U V} {
    lassign $U x y z
    lassign $V u v w
    list $(($y*$w - $v*$z)) $(($w*$x - $u*$z)) $(($x*$v - $u*$y))
}
# plain Tcl
proc dotPlain {U V} {set s 0; foreach u $U v $V {set s [expr {$s + $u*$v}]}; set s}

# TIP 672
proc dot672 {U V} {set s 0; foreach u $U v $V {set s $(($s + $u*$v))}; set s}
# plain Tcl
proc tensorPlain {U V} {lmap u $U {lmap v $V {expr {$u * $v}}}}

# TIP 672 (an lmap body is a script, so it needs a command around the value)
proc tensor672 {U V} {lmap u $U {lmap v $V {set _ $(($u * $v))}}}
# plain Tcl
proc rotPlain {deg} {
    set a [expr {$deg/180.0*acos(-1)}]
    list [expr {cos($a)}] [expr {sin($a)}] [expr {-sin($a)}] [expr {cos($a)}] 0 0
}

# TIP 672
proc rot672 {deg} {
    set a $(($deg/180.0*acos(-1)))
    list $((cos($a))) $((sin($a))) $((-sin($a))) $((cos($a))) 0 0
}
# plain Tcl
proc distPlain {x0 y0 x1 y1} {expr {hypot($x1-$x0, $y1-$y0)}}

# TIP 672 (a proc body ends with a command, so it needs `return`)
proc dist672 {x0 y0 x1 y1} {return $((hypot($x1-$x0, $y1-$y0)))}
# plain Tcl
proc polyPlain {c1 c2} {
    set out [lrepeat [expr {[llength $c1]+[llength $c2]-1}] 0]
    set i 0
    foreach a $c1 {
        set j 0
        foreach b $c2 {
            lset out [expr {$i+$j}] [expr {[lindex $out [expr {$i+$j}]] + $a*$b}]
            incr j
        }
        incr i
    }
    set out
}

# TIP 672
proc poly672 {c1 c2} {
    set out [lrepeat $(([llength $c1]+[llength $c2]-1)) 0]
    set i 0
    foreach a $c1 {
        set j 0
        foreach b $c2 {
            lset out $(($i+$j)) $(([lindex $out $(($i+$j))] + $a*$b))
            incr j
        }
        incr i
    }
    set out
}
proc calculate_edge_distance_672 {px py t1 t2 t3} {
    set edges [list [list $t1 $t2] [list $t2 $t3] [list $t3 $t1]]
    set min_distance 999999999
    foreach edge $edges {
        lassign $edge p1 p2
        lassign $p1 x1 y1
        lassign $p2 x2 y2
        set A $(($y2-$y1))
        set B $(($x1-$x2))
        set C $(($x2*$y1 - $x1*$y2))
        set distance $((abs($A*$px + $B*$py + $C) / hypot($A, $B)))
        if {$distance < $min_distance} {set min_distance $distance}
    }
    return $(([point_in_triangle $px $py $t1 $t2 $t3] ? -$min_distance : $min_distance))
}
set U {1.5 2 3}; set V {4 5.5 6}
puts "cross: [expr {[crossPlain $U $V] eq [cross672 $U $V]}]"
puts "dot: [expr {[dotPlain $U $V] eq [dot672 $U $V]}]"
puts "tensor: [expr {[tensorPlain $U $V] eq [tensor672 $U $V]}]"
puts "rot: [expr {[rotPlain 30] eq [rot672 30]}]"
puts "dist: [expr {[distPlain 1 2 4 6] eq [dist672 1 2 4 6]}]"
set w 7; set h 3; set a(2) two
puts "area=$(($w*$h)) perimeter=$((2*($w+$h)))"
puts "array: $a($((1+1)))"
if {$(($w % 2)) == 1} {puts "w is odd"}
puts [format "%.2f" $((3.14159*$w*$w))]
