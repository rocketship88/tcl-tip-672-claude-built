import random, subprocess, sys, os
MODE = int(sys.argv[1]); N = int(sys.argv[2]); seed = int(sys.argv[3]) if len(sys.argv)>3 else 1
random.seed(seed)
ALPHA = list("()()()[]{}\"\"\\\\ $ab1+*;\n") + ["\x00","\xc3\xa9".encode('latin1').decode('latin1'),"\xe2\x82\xac"]
def rnd_body():
    k = random.choice([0,1,2,3,5,8,12,20,40])
    return "".join(random.choice(ALPHA) for _ in range(k))
def gen():
    r = random.random()
    pre = "$((" if MODE == 2 else random.choice(["$(","$(("])
    if r < 0.15:       # structured-ish: nested constructs
        parts = []
        for _ in range(random.randint(1,6)):
            parts.append(random.choice(["1","+","(2*3)","{)}","\")\"","[set x )]","\\)","[a \"]\"]","(","x"]))
        body = "".join(parts)
    else:
        body = rnd_body()
    tail = random.choice(["))", ")", "", "))x", ")) ", "))("]) 
    return pre + body + tail
# ---- independent reference (written from the spec, not from the C code) ----
def scan(s, i, closer):
    """index of first unnested closer at/after i, or None. i is just past the opener."""
    depth = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c == '\\':
            i += 2; continue            # skip escaped char (or run off the end)
        if c == '{':
            lvl = 1; i += 1
            while i < n and lvl:
                if s[i] == '\\': i += 2; continue
                if s[i] == '{': lvl += 1
                elif s[i] == '}': lvl -= 1
                i += 1
            if lvl: return None
            continue
        if c == '"':
            i += 1
            while i < n and s[i] != '"':
                if s[i] == '\\': i += 2; continue
                if s[i] == '[':
                    j = scan(s, i+1, ']')
                    if j is None: return None
                    i = j
                i += 1
            if i >= n: return None
            i += 1; continue
        if c == '[':
            j = scan(s, i+1, ']')
            if j is None: return None
            i = j + 1; continue
        if c == '(' and closer == ')': depth += 1
        elif c == ')' and closer == ')':
            if depth == 0: return i
            depth -= 1
        elif c == ']' and closer == ']':
            return i
        i += 1
    return None
def expect(s):
    """-> (ok?, incomplete, consumed) for a string starting with the trigger."""
    skip = 2 if s.startswith("$((") and MODE == 2 else (1 if MODE == 1 else 2)
    if MODE == 1: skip = 2 if s.startswith("$((") else 1      # "$((" still reads as "$(" + body "(...)"
    if MODE == 1:
        e = scan(s, 1+1 if False else 2, ')')     # body starts after "$("
        if e is None: return (False, 1, None)
        return (True, 0, e + 1)
    e = scan(s, 3, ')')
    if e is None: return (False, 1, None)
    if e + 1 >= len(s): return (False, 1, None)
    if s[e+1] != ')': return (False, 0, None)       # syntax error, not incomplete
    return (True, 0, e + 2)
cases = [gen() for _ in range(N)]
# the C harness works in raw bytes; Latin-1 chars above are written out as UTF-8 bytes
raw = [c.encode('utf-8', 'surrogatepass') if False else c.encode('latin1', 'ignore') for c in cases]
# make multi-byte sequences real UTF-8: re-encode é and euro by hand
def enc(c): return c.replace("\xc3\xa9", "\xc3\xa9")
with open(f"cases_{MODE}.hex", "w") as f:
    for r in raw: f.write(r.hex() + "\n")
bad = 0; counts = {"ok":0,"incomplete":0,"syntax":0}
out = subprocess.run([f"./harness_{MODE}", f"cases_{MODE}.hex"], capture_output=True, text=True)
if out.returncode != 0 or "AddressSanitizer" in out.stderr:
    print("HARNESS FAILED/ASAN:", out.stderr[:1500]); sys.exit(2)
lines = out.stdout.splitlines()
assert len(lines) == len(raw), (len(lines), len(raw))
for c, r, l in zip(cases, raw, lines):
    s = r.decode('latin1')
    rc, inc, et, t0, size, ntok = map(int, l.split())
    ok, incomplete, consumed = expect(s)
    if ok:
        counts["ok"] += 1
        # token 0 is TCL_TOKEN_VARIABLE (type 8?) whose size is the whole "$...)" run
        if not (rc == 0 and size == consumed):
            bad += 1; print("MISMATCH ok-case", repr(s), "C:", l, "ref consumed:", consumed)
    else:
        counts["incomplete" if incomplete else "syntax"] += 1
        if rc == 0 and MODE == 2 and s.startswith("$((") :
            bad += 1; print("MISMATCH expected error", repr(s), "C:", l)
        elif MODE == 2 and rc != 0 and bool(inc) != bool(incomplete):
            bad += 1; print("MISMATCH incomplete flag", repr(s), "C:", l, "ref incomplete:", incomplete)
        elif MODE == 1 and rc == 0:
            bad += 1; print("MISMATCH expected error", repr(s), "C:", l)
print(f"mode {MODE}: {N} cases, {counts}, mismatches: {bad}")
sys.exit(1 if bad else 0)
