# Scripts used (paths are the ones used in the sandbox; adjust `/root/...` as needed)

* `mutation/` - mutation-testing harness: `gen.py` (makes `mutants.json`), `run.py <1|2>` (builds and tests each mutant, appends to `results<N>.jsonl`, resumable), `start.sh` (restarts a dead worker; used by the 10-minute check-ins), `summary.py` (totals), `baseline*.json`, progress and worker logs. Results: `../mutation/results*.jsonl`.
* `windows/` - `buildmerge_exprsubst.bat` (your build script with the `EXPRSUBST` block added) and `test.bat 1|2`.
* `probes/` - the small Tcl probes used during development (`probe.tcl`, `t1.tcl`, `exp*.tcl`), the first draft of the new tests, and `counts.txt` (the line-count table source).
* `valgrind_asan_mem/` - `run1.sh` plus `build_recipes.sh` listing the configure lines for the ASan, memory-debug, Valgrind and performance builds.
* Performance scripts: `../performance/`; Valgrind logs: `../valgrind/`.
