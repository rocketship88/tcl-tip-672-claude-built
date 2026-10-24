# Workload that runs on every build: parse/compile and runtime-subst of ordinary scripts
set stmts {}
for {set k 0} {$k < 200} {incr k} {
    append stmts "set a$k \$x; set b$k \$arr(key$k); set c$k \${y}; set d$k \"v=\$x/\$y\[string length \$x\]\"; set e$k \$::g(\$x); expr {\$x+\$y*$k}\n"
}
set sub {}
for {set k 0} {$k < 200} {incr k} { append sub "A=\$x B=\$arr(k) C=\${y} D=\[string length \$x\] E=\$::g(i)\\n " }
array set arr {k 1}; array set ::g {i 2 5 3}
set x 5; set y 6
set N [expr {$argc ? [lindex $argv 0] : 50}]
for {set i 0} {$i < $N} {incr i} {
    proc p$i {} "$stmts\n#$i"
    catch {p$i}
    catch {subst [string cat $sub $i]}
    catch {eval [string cat $stmts $i]}
    rename p$i {}
}
