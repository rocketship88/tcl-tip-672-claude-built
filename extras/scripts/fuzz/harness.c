/* Reads lines "<hex>" from argv[1] (each = one input, raw bytes), parses with
 * Tcl_ParseVarName on an exactly-sized heap buffer, prints:
 *   rc incomplete errorType firstTokenType firstTokenSize numTokens */
#include <tcl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int hexv(int c){return c<='9'?c-'0':(c|32)-'a'+10;}
int main(int argc, char **argv)
{
    FILE *f = fopen(argv[1], "r");
    char line[8192];
    Tcl_FindExecutable("fuzz");
    while (fgets(line, sizeof line, f)) {
        size_t hl = strcspn(line, "\r\n"), n = hl / 2, i;
        char *buf = malloc(n ? n : 1);
        Tcl_Parse p;
        for (i = 0; i < n; i++) buf[i] = (char)(hexv(line[2*i])*16 + hexv(line[2*i+1]));
        int rc = Tcl_ParseVarName(NULL, buf, (Tcl_Size)n, &p, 0);
        printf("%d %d %d %d %d %d\n", rc, p.incomplete, p.errorType,
               p.numTokens ? p.tokenPtr[0].type : -1,
               p.numTokens ? (int)p.tokenPtr[0].size : -1, (int)p.numTokens);
        Tcl_FreeParse(&p);
        free(buf);
    }
    return 0;
}
