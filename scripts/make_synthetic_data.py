#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate a structurally-identical synthetic probe dataset.

No real resource URLs or payee addresses are used: every address-like field is
derived from a counter through SHA-256, so the output has the same schema, the
same categorical distribution shape, and zero attribution value.

Usage:
    python scripts/make_synthetic_data.py --rows 600 --out data/synthetic.csv
"""
import argparse
import csv
import hashlib
import random

STATES = ["CHALLENGE"] * 586 + ["ERR"] * 11 + ["HTTP_503"] * 6 + ["HTTP_404"] * 4 + \
         ["NO_402"] * 3 + ["HTTP_400"] * 2 + ["HTTP_502"] * 2 + ["HTTP_401"] * 1 + \
         ["HTTP_525"] * 1 + ["HTTP_422"] * 1
GAPS = ["A_out"] * 357 + ["no_payee"] * 229 + [""] * 31
FIELDS = ["resource", "host", "probe_state", "method", "via", "payees",
          "payee_in_registry", "gap_type"]


def h(prefix, n):
    return prefix + hashlib.sha256(f"synthetic:{n}".encode()).hexdigest()[:40]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=600)
    ap.add_argument("--out", default="data/synthetic.csv")
    ap.add_argument("--seed", type=int, default=20261004)
    a = ap.parse_args()
    random.seed(a.seed)

    with open(a.out, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for i in range(a.rows):
            state = random.choice(STATES)
            gap = random.choice(GAPS) if state == "CHALLENGE" else ""
            has_payee = gap == "A_out"
            w.writerow({
                "resource": h("https://synth.invalid/r/", i),
                "host": f"host{i % 37:02d}.synth.invalid",
                "probe_state": state,
                "method": "GET" if i % 3 else "POST",
                "via": random.choice(["direct", "proxy", "direct"]),
                "payees": h("0x", i) if has_payee else "",
                "payee_in_registry": "0" if has_payee else "",
                "gap_type": gap,
            })
    print(f"wrote {a.rows} synthetic rows -> {a.out}")


if __name__ == "__main__":
    main()
