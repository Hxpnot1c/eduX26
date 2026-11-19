"""Check verify_sim.FastBackend (graded Verify) against the PATCHED learner code (RealBackend on the w4-fix-verify copy).

  EDUX_DATA_DIR=<fresh dir with content.db loaded> PYTHONPATH=<patched copy>:../literacy:. python verify_validate.py [n]
"""
import sys

import lit_model as M
import verify_sim as V

n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
worst, compared = 0.0, 0
for vname in ("missing+graded", "fix (missing+graded+found)"):   # the patched code is always graded
    cfg = V.VARIANTS[vname]
    for noise in (M.Noise(), M.Noise.symmetric(0.2)):
        for g in M.GROUPS:
            for k in range(n):
                seed = 500 + k
                fast = V._wrapped(M.run_student, V.FastBackend(cfg), cfg, g, seed, noise, "mnar")
                real = V._wrapped(M.run_student, M.RealBackend(cfg, f"v{vname[:3]}{g}{k}{noise.fn}"), cfg, g, seed, noise, "mnar")
                for a, b in zip(fast["reads"], real["reads"]):
                    for key in ("ask", "verify", "how"):
                        worst = max(worst, abs(a[key] - b[key]))
                        compared += 1
print(f"compared {compared} weekly values; max |fast - real| = {worst:.2e}")
