proc t {label script} {
    set c [catch {uplevel #0 $script} r]
    puts [format "%-34s %s -> %s" $label $c [string map {\n { }} $r]]
}
set x 5; set s {$x}; set a(1) one; set a(k) kay
t {bare word}            {set v $((1+2))}
t {in quotes}            {set v "n=$((3*4))!"}
t {between text}         {set v a$((1+1))b$((2+2))c}
t {extra parens}         {set v $(((1+2)*3))}
t {var in body}          {set v $(($x*2))}
t {no double subst}      {set v $(("$s" eq "\$x"))}
t {cmd in body}          {set v $(([string length abc]+1))}
t {braces in body}       {set v $(([llength {a b )}]))}
t {quote w/ paren}       {set v $(([string length ")"]))}
t {nested dollar-expr}   {set v $(($((1+1))+1))}
t {inside brackets}      {set v [list $((1+1)) $((2+2))]}
t {array index}          {set v $a($((0+1)))}
t {in subst}             {subst {r=$((6*7))}}
t {in expr}              {expr {$((2+3))*2}}
t {math func}            {set v $((max(3,9)))}
t {float}                {set v $((1/3.0))}
t {string result}        {set v $(("a" . "b"))}
t {syntax err}           {set v $((1+))}
t {unterminated}         {set v $((1+2)}
t {old: empty array}     {set () E; set v $()}
t {old: dollar paren}    {set v $(x)}
t {proc compiled} {
    proc p {n} {return "<$((\$n+1))>"}
    p 4
}
t {proc compiled2} {
    proc p2 {n} {set r "x"; append r $(($n*$n)); return $r}
    p2 7
}
t {list/expand}          {set v [list {*}$((1+1)) b]}
t {if cond}              {if {$((1+1)) == 2} {set v yes}}
t {catch non-ok in body} {set v $(([return -code error boom]))}
