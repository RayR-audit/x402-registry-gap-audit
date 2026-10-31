# x402 Registry-Gap Audit — Reproduction Package

Reproduction kit for the audit *x402 Payment Infrastructure: Registry-Gap Audit (v0.2, 2026-10-04)*.

This repository exists so that a reader can **re-run the measurement path** that produces the
numbers in the report, instead of taking them on trust. It contains the probing scripts, the
scoring logic, and the report itself. It deliberately does **not** contain the raw production
dataset.

## What this package lets you verify

| Question a reader may ask | Where it is answered |
|---|---|
| How was each resource probed? | `registry_gap/probe_type_a*.py` |
| What counts as a "Type A" gap? | `registries/VERSIONS.md` (definition + known limits) |
| Can the aggregation be re-run end-to-end? | `scripts/verify_coverage.py` |
| What does the per-row output look like? | `data/probe_results_v3_hashed.csv` |
| Why are there no raw addresses? | see *Data policy* below |

## Quick start

```bash
pip install -r requirements.txt

# 1) generate a structurally-identical synthetic dataset (no real addresses)
python scripts/make_synthetic_data.py --rows 600 --out data/synthetic.csv

# 2) run the aggregation path on it
python scripts/verify_coverage.py --csv data/synthetic.csv --expect-synthetic
```

`verify_coverage.py` prints the `probe_state` / `gap_type` distributions and the derived
"unregistered-payee share" exactly as the report computes it. On synthetic input the numbers are
meaningless by construction — the point is that the **computation path is executable and auditable**.

To reproduce the report's figures you need the real dataset; see *Data policy*.

## Data policy (read this before filing an issue)

- **Real payee addresses are not published here.** The per-row file in `data/` is a *hash
  derivative*: every `resource` and `payee` is replaced by a truncated SHA-256 digest, so rows can
  be joined and counted but not attributed to a party.
- The underlying raw dataset scores ~87k on-chain addresses individually. Publishing it would
  amount to naming parties, which this project does not do — the audit's unit of analysis is the
  **structure of the gap**, not the identity of the actors.
- Access to the raw dataset is available on request under an agreement that the recipient will not
  deanonymise individual participants.

## Scope and limits (carried verbatim from the report)

- The facilitator registry used is a frozen upstream snapshot (last upstream update 2026-04-14).
  Facilitators that appeared after that date are outside the registry and therefore cannot be
  classified as registered — every citation of these figures must carry this limit.
- The classification concerns **settlement-path attribution only**. It is not a judgement about
  service quality, honesty, or intent of any operator.
- Definitions, versioning discipline, and the list of downstream artefacts affected by any change
  live in `registries/VERSIONS.md`.

## Contents

```
audits/      the audit report (v0.1 + v0.2, markdown; v0.2 also as PDF)
scorecard/   the public scorecard page (v1.0)
notes/       Data Note #1 (preliminary), previously published separately
registry_gap/ the probing scripts (the evidence that the finding is measured, not derived)
registries/  measurement definitions and version history
data/        hashed per-row output + aggregate summary
scripts/     synthetic-data generator and the aggregation/verification path
```

## Licence

See `LICENSE`.

## Related record

This package accompanies **x402 Allocation Readiness Audit — v0.2** (Zenodo, 2026-10-04):
<https://doi.org/10.5281/zenodo.23125475>

**Do not compare the two headline numbers.** The *unregistered-payee share* reported here
(`A_out / (A_out + no_payee)` over CHALLENGE settlements, 357 / 586 = 60.9%) is a
registry-coverage metric. The "at most 84.1%" figure in the data note is a
behavioural-fingerprint **bound on the share of settlement count** attributable to coordinated
operator cohorts — a different numerator over a different denominator (addresses, not CHALLENGE
rows). The two are not comparable and must not be placed in the same sentence.

