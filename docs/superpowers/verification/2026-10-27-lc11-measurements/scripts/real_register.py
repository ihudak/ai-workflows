#!/usr/bin/env python3
"""Drive the REAL register.py (read from /workspace/ai-workflows, never modified) through its own
selftest helpers, so a scenario can commit genuine run records on two clones.
  real_register.py code <dir>                                   -> creates a code repo, prints its commit
  real_register.py scan <specs> <code> <folder> <pid> <path> <line> <at>  -> scan + plan + commit, prints the record"""
import importlib.util, json, os, sys

REG = "/workspace/ai-workflows/plugins/security-workflows/scripts/register.py"
spec = importlib.util.spec_from_file_location("register", REG)
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)

cmd = sys.argv[1]
if cmd == "code":
    repo, c1 = r._repo(sys.argv[2])
    print(c1)
elif cmd == "scan":
    specs, code, folder, pid, path, line, at = sys.argv[2:9]
    c = r._g(code, "rev-parse", "HEAD")
    r._scan(specs, folder, c, [(pid, path, int(line), "CWE-89", "HIGH")])
    p = r.plan(specs, "code", code, folder, None, at[:10])
    res = r.commit(specs, "code", p, {}, "Tester", "scan", None, at)
    print(json.dumps({"record": os.path.basename(res["record"]), "ids": res.get("ids"), "renumbered": res.get("renumbered")}))
