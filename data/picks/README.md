# Atlas Stock Picks — Tracking Log

This directory contains Atlas's historical stock picks, saved as markdown files.

## File Naming Convention

```
YYYYMMDD_TICKER_Xconv.md
```

Example: `20260414_NVDA_8conv.md` — NVDA pick generated April 14 2026, conviction 8/10.

## Pick Lifecycle

| Stage | Action | How |
|-------|--------|-----|
| Generated | Atlas saves file here via `--save` flag | Automatic |
| Entered | CC notes actual entry price/date | Edit the file manually |
| Monitoring | Review weekly vs catalyst calendar | `/pick status` (planned) |
| Exited | CC notes exit price/date/reason | Edit the file manually |
| Post-mortem | Record actual vs expected outcome | Edit the file manually |

## Tracking a Pick

At the bottom of each `.md` file, add a tracking section when you enter/exit:

```markdown
## Live Tracking
- **Entry date:** 2026-04-14
- **Actual entry price:** $XXX.XX
- **Exit date:** —
- **Actual exit price:** —
- **P&L:** —
- **Notes:** —
```

## Performance Review

Run a pick review with:
```bash
python -m research.stock_picker --review  # coming soon
```

## Tax Notes

- **TFSA picks:** Gains are 100% tax-free. Prioritize high-growth US equities here.
- **Non-Reg picks:** Capital gains have 50% inclusion rate in Canada.
  Hold > 1 year to classify as capital gains (not business income).
- **RRSP picks:** Best for US dividend stocks (15% withholding tax waived under treaty).
