#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Re-run the aggregation path used in the audit and print the derived figures.

This is the executable definition of the numbers in the report. Anything the
report states about coverage must be reproducible by running this file on the
same input.

Usage:
    python scripts/verify_coverage.py --csv data/probe_results_v3_hashed.csv
    python scripts/verify_coverage.py --csv data/synthetic.csv --expect-synthetic

Definitions (mirroring registries/VERSIONS.md):
    probe_state == CHALLENGE      -> the resource returned an x402 payment challenge
    gap_type   == A_out           -> a settlement-layer payee was observed that is
                                     NOT present in the frozen facilitator registry
    gap_type   == no_payee        -> challenge observed, no payee extractable
    unregistered-payee share      -> A_out / (A_out + no_payee) among CHALLENGE rows
"""
import argparse
import collections
import csv
import sys


def load(path):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--expect-synthetic", action="store_true",
                    help="assert the input is the synthetic dataset (no real addresses)")
    a = ap.parse_args()

    rows = load(a.csv)
    if not rows:
        print("EMPTY INPUT"); return 2

    states = collections.Counter((r.get("probe_state") or "").strip() for r in rows)
    gaps = collections.Counter((r.get("gap_type") or "").strip() for r in rows
                               if (r.get("probe_state") or "").strip() == "CHALLENGE")

    # synthetic-safety assertion: forbidden markers of real data
    if a.expect_synthetic:
        bad = [r for r in rows if ".invalid" not in (r.get("host") or "")]
        if bad:
            print(f"REFUSED: {len(bad)} rows do not look synthetic (host lacks .invalid)")
            return 3

    a_out, no_payee = gaps.get("A_out", 0), gaps.get("no_payee", 0)
    denom = a_out + no_payee
    share = (a_out / denom * 100) if denom else 0.0

    print(f"rows                : {len(rows)}")
    print(f"probe_state         : {dict(states.most_common())}")
    print(f"gap_type (CHALLENGE): {dict(gaps.most_common())}")
    print(f"challenge rows      : {states.get('CHALLENGE', 0)}")
    print(f"unregistered-payee share = {a_out}/{denom} = {share:.1f}%")

    if a.expect_synthetic:
        print("\n[synthetic input] these figures are meaningless by construction —")
        print("the assertion being demonstrated is that the computation path executes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
