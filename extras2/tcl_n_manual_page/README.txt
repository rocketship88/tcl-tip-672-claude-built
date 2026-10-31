TIP 672: proposed change to the Tcl(n) manual page (doc/Tcl.n)
==============================================================

Tcl_n_with_672.html   The whole Tcl(n) page, with a clickable contents outline.
                      Red = text added by TIP 672. Red and underlined = existing text
                      that changes. Self-contained (no external files), so it can be
                      served as is.
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
The Fossil branch tip-672-v2 carries the Oct 30 wording (check-in b5136123e7); the Oct 31 opening paragraph is a later commit.
The other manual pages the patch touches (subst.n, ParseCmd.3, SubstObj.3) are unchanged.

The HTML was rendered with groff from the nroff source, left-aligned, so line breaks can
differ a little from the installed man page.
