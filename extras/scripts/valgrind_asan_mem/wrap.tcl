# usage: tcltest wrap.tcl memflag testfiles...
set memflag [lindex $argv 0]
set files [lrange $argv 1 end]
if {$memflag} { memory trace off }
set argv [list -singleproc 1 -testdir /root/tcl-trunk/tests -file $files]
set argc [llength $argv]
source /root/tcl-trunk/tests/all.tcl
if {$memflag} {
    set f /tmp/memactive.[pid]
    memory active $f
    set n [llength [split [string trim [exec cat $f]] \n]]
    puts "MEMACTIVE lines: $n"
}
