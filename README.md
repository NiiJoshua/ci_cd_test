# data-pipeline-cicd-demo

A tiny data-engineering ETL pipeline wired up with **GitHub Actions** — built for
**Module 12: CI/CD & Workflow Automation**. It is intentionally small so the
focus stays on the CI/CD mechanics, not the data logic.

The pipeline: **extract** a CSV → **validate** against a data contract →
**transform** (normalise) → **load** to an output CSV (idempotently).

---

## Quick start (local)

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# run the tests
pytest                      # everything
pytest -m "not integration" # just the fast unit tests

# run the pipeline
python -m src.etl.pipeline --input data/raw/customers_raw.csv --output data/out/customers_clean.csv
```

## What to push to GitHub, and what to watch

1. Create an empty repo on GitHub, then from this folder:
   ```bash
   git init && git add . && git commit -m "Initial ETL + CI/CD"
   git branch -M main
   git remote add origin https://github.com/<you>/data-pipeline-cicd-demo.git
   git push -u origin main
   ```
2. Open the repo's **Actions** tab. You'll see the **CI** workflow start
   automatically, with its jobs running in order: `lint → unit-tests → integration`.
3. Make a change on a branch, push it, and open a **Pull Request** into `main`.
   The PR page shows the CI checks; a red ✗ blocks the merge, a green ✓ allows it.
4. Merge the PR. Now the **CD** workflow runs: it re-checks the gate, then does
   the (mock) deploy.

The two step-by-step notebooks that ship with this module walk through every one
of these screens in detail.

## How this maps to the four focus areas

| Focus area | Where to see it |
|---|---|
| **Idempotency & safe re-runs** | `src/etl/load.py` (upsert by `customer_id`) + `tests/test_idempotency.py` (re-run → identical file) |
| **Manual/ad-hoc vs. automated gating** | `.github/workflows/ci.yml` (`needs:` chains) + branch protection requiring the CI checks |
| **Testing strategy: speed vs. coverage** | fast unit tests (`pytest -m "not integration"`) vs. the full suite; matrix across Python versions |
| **Rollback & versioning** | `VERSION` file, release tags (`v*`), and `cd.yml`'s `workflow_dispatch` → `rollback_to` |

## Layout

```
├── src/etl/            extract, validate, transform, load, pipeline
├── tests/              unit tests (fast) + integration tests (slower)
├── data/raw/           sample input (customers_raw.csv, customers_bad.csv)
├── .github/workflows/  ci.yml (push/PR) and cd.yml (merge/tag/manual)
├── VERSION             current version, for the versioning/rollback demo
├── requirements.txt
└── pyproject.toml      pytest markers + ruff config
```

## Recommended repo settings (do these once on GitHub)

- **Settings → Branches → Add branch protection rule** for `main`: require the
  CI status checks to pass and require a PR before merging. *This is what turns
  "please remember to run tests" into an enforced, automated gate.*
- **Settings → Environments → `production`**: add a **required reviewer** so the
  `deploy` job in CD pauses for human approval.
