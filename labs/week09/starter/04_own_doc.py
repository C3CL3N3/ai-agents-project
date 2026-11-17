"""Homework: run the sweep on one document of your own, photographed.

    python 04_own_doc.py path/to/photo.jpg
    python 04_own_doc.py path/to/photo.jpg --total 1498.54   # if you know it

There is no ground truth for your own photo, so the table shows what came
back and which checks fired, per variant. Pass --total (the real total,
read by you) and each row also says whether the total read is right.
Compare the rows with the sweep on INV-001 to INV-005 in DECISIONS.md.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from checks import GROUPS, run_checks
from perturb import SWEEP
from vision import read_group

from project.trace import write_json


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--total", type=float, default=None,
                    help="the true total, if you read it yourself")
    args = ap.parse_args()
    image = Path(args.image)

    rows = []
    print(f"{'variant':<22}{'total read':>12}{'right?':>8}{'s':>7}  "
          f"checks fired / failures")
    print("-" * 90)
    for variant in SWEEP:
        fields, failures, seconds = {}, [], 0.0
        for group, names in GROUPS.items():
            res = read_group(image, group, names, variant=variant)
            seconds += res.elapsed_s
            if res.ok:
                fields.update(res.fields)
            else:
                failures.append(res.failure)
                fields.update({n: None for n in names})
        report = run_checks(fields)
        total = report.parsed["total"]
        right = ("-" if args.total is None or total is None
                 else "yes" if abs(total - args.total) < 0.01 else "NO")
        note = "; ".join(failures + report.fired)[:44]
        print(f"{variant:<22}{str(total):>12}{right:>8}{seconds:>7.1f}  {note}")
        rows.append({"variant": variant, "fields": fields,
                     "fired": report.fired, "failures": failures,
                     "total_right": right, "seconds": round(seconds, 1)})

    write_json("artifacts/week09_own_doc.json",
               {"image": image.name, "true_total": args.total, "rows": rows})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
