---
name: data-access
description: How to query the DataOS database directly - table schemas and example SQL
---

# Data Access (DataOS)

This is the reference for the local business data warehouse DataOS builds. Read this before running any direct query against the database.

## The SQLite Data Warehouse

- **Location:** `data/data.db` (SQLite, gitignored — never committed)
- **Connect from Python:**
  ```python
  import sqlite3
  conn = sqlite3.connect("data/data.db")
  conn.row_factory = sqlite3.Row
  ```
- Claude can run SQL directly in a session by writing a short Python script with the snippet above, or via `scripts/db.py`'s helpers (`query_one`, `query_all`).

## Connected Data Sources

| Source | Table(s) | Collection script | What it tracks |
|--------|----------|--------------------|-----------------|
| FX rates (starter, no auth needed) | `fx_rates` | `scripts/collect_fx_rates.py` | Daily USD exchange rates against GBP, EUR, CAD, AUD, JPY |

No business-revenue or traffic sources are connected yet — Cool Hollow Coaching is pre-launch (no live Stripe, no Instagram/YouTube page, no GA4 traffic). Add a real collector the moment any of those go live; see "Adding a New Source" below.

## Table Schemas

### `fx_rates`
| Column | Type | Description |
|--------|------|--------------|
| `date` | TEXT | Date of the rate snapshot (YYYY-MM-DD) |
| `currency` | TEXT | Target currency code (e.g. GBP, EUR) |
| `rate` | REAL | Exchange rate from 1 USD |
| `base` | TEXT | Base currency, always `USD` |
| `collected_at` | TEXT | UTC timestamp the row was written |

Primary key: (`date`, `currency`)

### `collection_log`
Every collection run is logged here regardless of source, useful for debugging.

| Column | Type | Description |
|--------|------|--------------|
| `id` | INTEGER | Auto-increment row id |
| `collected_at` | TEXT | UTC timestamp |
| `source` | TEXT | Collector name (e.g. `fx_rates`) |
| `status` | TEXT | `success`, `skipped`, `error`, or `exception` |
| `reason` | TEXT | Why a source was skipped or errored (nullable) |
| `records_written` | INTEGER | Row count written by that run |

## Common Queries

Latest snapshot for a source:
```sql
SELECT * FROM fx_rates WHERE date = (SELECT MAX(date) FROM fx_rates);
```

Trend over the last 30 days:
```sql
SELECT date, currency, rate FROM fx_rates
WHERE date >= date('now', '-30 days')
ORDER BY date, currency;
```

Most recent collection run per source:
```sql
SELECT source, status, reason, records_written, MAX(collected_at) as last_run
FROM collection_log
GROUP BY source;
```

## Adding a New Source

When a real data source goes live (Stripe, Instagram via a third-party API, a P&L spreadsheet, etc.):

1. Run `/install module-installs/data-os-v1` again, or just ask Claude to "connect [source] to DataOS"
2. Claude follows the same pattern as `collect_fx_rates.py`: a `collect()` function that fetches data, and a `write(conn, result, date)` function that stores it
3. The new `collect_<name>.py` file is auto-discovered by `scripts/collect.py` — no orchestrator changes needed
4. Add a `section_<name>(conn)` function to `scripts/generate_metrics.py` so the new metric shows up in `context/group/key-metrics.md`
5. Update this file with the new table's schema and a couple of example queries

## Running Collection Manually

```bash
.venv/bin/python scripts/collect.py              # run all collectors
.venv/bin/python scripts/collect.py --sources fx_rates   # run one source
.venv/bin/python scripts/generate_metrics.py      # regenerate key-metrics.md only
```

Daily automation (when set up) runs this at 6:00 AM and writes to `data/collect.log`.
