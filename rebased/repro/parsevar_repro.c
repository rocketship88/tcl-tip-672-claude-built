#include <tcl.h>
#include <stdio.h>
#include <string.h>
/* Florent's two patterns, with variables and with expressions. */
int main(int argc, char **argv) {
    Tcl_Interp *interp;
    const char *a, *b, *v;
    char abuf[64];
    (void)argc;
    Tcl_FindExecutable(argv[0]);
    interp = Tcl_CreateInterp();
    Tcl_Eval(interp, "set x 10; set y 20");

    /* pattern 1: two calls, use both */
    a = Tcl_ParseVar(interp, "$x", NULL); strncpy(abuf, a, 63);
    b = Tcl_ParseVar(interp, "$y", NULL);
    printf("vars : a=<%s> b=<%s>\n", a, b);
    a = Tcl_ParseVar(interp, "$((1000+1))", NULL);
    b = Tcl_ParseVar(interp, "$((2000+2))", NULL);
    printf("exprs: a=<%s> b=<%s>\n", a ? a : "(null)", b ? b : "(null)");

    /* pattern 2: append the returned string to the result */
    Tcl_ResetResult(interp);
    v = Tcl_ParseVar(interp, "$x", NULL);
    Tcl_AppendResult(interp, "value is ", v, " (ok)", NULL);
    printf("var : %s\n", Tcl_GetStringResult(interp));
    Tcl_ResetResult(interp);
    v = Tcl_ParseVar(interp, "$((1000+1))", NULL);
    Tcl_AppendResult(interp, "value is ", v ? v : "(null)", " (ok)", NULL);
    printf("expr: %s\n", Tcl_GetStringResult(interp));
    return 0;
}
