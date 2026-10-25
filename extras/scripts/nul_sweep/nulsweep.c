/* Parse every prefix of a corpus, with raw 0 bytes injected at every position,
 * from an exactly-sized heap block (no terminator). ASan flags any over-read. */
#include <tcl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static long calls = 0, ok = 0, err = 0, inc = 0;

static void one(const char *s, int n, int mode)
{
    /* mode 0: exact size, nothing after it. mode 1: Tcl_ParseCommand's contract: a terminator follows. */
    char *buf = malloc(n + 1);
    if (mode == 0) { free(buf); buf = malloc(n ? n : 1); }
    Tcl_Parse p;
    int rc;
    memcpy(buf, s, n);
    if (mode == 1) { buf[n] = 0; }
    calls++;
    if (getenv("TRACE")) { fprintf(stderr, "mode=%d n=%d [", mode, n); for (int i=0;i<n;i++) fprintf(stderr, buf[i]? "%c" : "<NUL>", buf[i]); fprintf(stderr, "]\n"); }
    if (mode == 0) {
        rc = Tcl_ParseVarName(NULL, buf, n, &p, 0);
    } else if (mode == 1) {
        rc = Tcl_ParseCommand(NULL, buf, n, 0, &p);
    } else {
        rc = Tcl_ParseVarName(NULL, buf, n, &p, 1);
    }
    if (rc == TCL_OK) ok++; else err++;
    if (p.incomplete) inc++;
    Tcl_FreeParse(&p);
    free(buf);
}

int main(void)
{
    static const char *corpus[] = {
        "$((1+2))", "$((1+2)", "$((1+2", "$((", "$(", "$(1+2)", "$(x)", "$((a)b)",
        "$((\"a)b\"))", "$(({a)b}))", "$(([set x 1]))", "$(([set x \"]\"]))",
        "$((\\)))", "$((1+(2*3)))", "$((1 ] 2))", "$(([", "$((\"", "$(({",
        "set a $((1+2)) b", "puts \"$((1+[expr 2]))\"", "$(($x+$y))", "$((é+1))",
        "$((\xe2\x82\xac))", "$((\xf0\x9f\x98\x80))", "x$((1))y", NULL
    };
    Tcl_FindExecutable("nulsweep");
    for (int c = 0; corpus[c]; c++) {
        int len = (int) strlen(corpus[c]);
        for (int n = 0; n <= len; n++) {
            for (int m = 0; m < 2; m++) {
                one(corpus[c], n, m);                       /* plain prefix */
                for (int z = 0; z < n; z++) {               /* raw NUL at z */
                    char tmp[128];
                    memcpy(tmp, corpus[c], n); tmp[z] = '\0';
                    one(tmp, n, m);
                }
            }
        }
    }
    printf("calls=%ld ok=%ld err=%ld incomplete=%ld\n", calls, ok, err, inc);
    return 0;
}
