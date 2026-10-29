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
Against the current page: 30 added source lines and 4 changed lines (34 insertions, 4 deletions in the diff).

extras/expr-subst.patch and new/doc/Tcl.n were regenerated (Oct 29) with this wording, so
the package agrees with itself. The Fossil branch (tip-672-v2) still carries the EARLIER
one-paragraph wording of this entry and the old rule [8] heading; it was not changed.
The other manual pages the patch touches (subst.n, ParseCmd.3, SubstObj.3) are unchanged.

The HTML was rendered with groff from the nroff source, left-aligned, so line breaks can
differ a little from the installed man page.
