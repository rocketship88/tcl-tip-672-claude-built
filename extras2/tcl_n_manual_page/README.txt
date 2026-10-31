TIP 672: proposed changes to the manual pages (Tcl.n, subst.n, ParseCmd.3, SubstObj.3)
=======================================================================================

Tcl_n_with_672.html   All the manual pages TIP 672 changes, in one page, in the style of the
                      TIP 759 doc-diff page: Tcl(n), subst(n), Tcl_ParseCmd(3) and Tcl_SubstObj(3).
                      Red = text added by TIP 672. Red and underlined = existing text that changes.
                      Removed text is not shown. Self-contained (the stylesheet is inline), so it
                      can be served as is. Links to other manual pages work only for the four
                      pages it contains.
Tcl.n.diff            The change as a unified diff against the current doc/Tcl.n.
Tcl.n.orig            doc/Tcl.n before the change (trunk).
Tcl.n.new             doc/Tcl.n with the change.

What changes in rule [8] (there is no new rule):
  - heading: "Variable substitution." becomes "Variable and expression substitution."
  - first sentence: "...by the value of a variable" becomes "...of a variable or of an expression"
  - the intro line says variable substitution takes the first three forms, and the fourth
    form is expression substitution
  - a fourth entry, $((expression)), after $name, $name(index) and ${name}, in four short
    paragraphs
Against the current page: 37 added source lines and 4 changed lines (41 insertions, 4 deletions in the diff).
The examples are written with spaces inside the delimiters, $(( $width * $height )), and the error paragraph
shows $(((1+2)*3)) and, with spaces, $(( (1+2)*3 )) as the two ways to write the corrected form.

extras/expr-subst.patch and new/doc/Tcl.n were regenerated with this wording, so the package agrees with itself.
The Fossil branch tip-672-v2 carries the Oct 30 wording (check-in b5136123e7); the Oct 31 opening paragraph is in check-in cfaf484bdb.
The other manual pages the patch touches (subst.n, ParseCmd.3, SubstObj.3) are in Tcl_n_with_672.html too;
their wording did not change in the Oct 31 round.

Tcl_n_with_672.html was rendered from the nroff source with the tcltk-man2html tool of the Tcl source tree, and
compared word by word with the same tool's output for the unmodified trunk (77ac0bb). Line breaks and fonts
follow the Tcl documentation style sheet, so it looks like the pages on the Tcl web site.
