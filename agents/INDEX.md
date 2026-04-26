# Atlas Agent Fleet

> Sub-agents Atlas dispatches for specialist work. Each is a Claude Code
> subagent with YAML frontmatter (name/description/model/tools) — invoke
> via the Agent tool with `subagent_type: <name>`.

| Agent | Model | Specialty |
|-------|-------|-----------|
| [tax-strategist](tax-strategist.md) | opus | Quarterly review, T1/T2 prep, GST/HST, CCPC timing, CRA correspondence |
| [portfolio-analyst](portfolio-analyst.md) | opus | Position sizing, rebalancing, account routing (TFSA/RRSP/FHSA/non-reg) |
| [research-analyst](research-analyst.md) | sonnet | SEC filings, 10-K/10-Q, fundamentals, historical analogs, thesis construction |
| [cashflow-monitor](cashflow-monitor.md) | sonnet | AR/AP aging, runway, burn drift, Montreal floor, pulse republish |
| [compliance-auditor](compliance-auditor.md) | opus | T1135, CCPC trigger, departure tax, cross-border, treaty residency |
| [behavioral-finance-guard](behavioral-finance-guard.md) | sonnet | Anti-FOMO/loss aversion/sunk cost. Cooling-off enforcer |
| [wealth-tracker](wealth-tracker.md) | sonnet | Net worth, FIRE projection, savings rate, jurisdictional-exit pacing |
| [debugger](debugger.md) | sonnet | Root-cause for tax math, reconciliation, API failures, pulse writes |

## Routing rules

- Tax question → `tax-strategist` (then `compliance-auditor` if cross-border)
- "Should I buy X?" → `behavioral-finance-guard` first → `research-analyst` → `portfolio-analyst`
- "What's my runway / am I on track?" → `cashflow-monitor` or `wealth-tracker`
- "Is incorporation worth it yet?" → `compliance-auditor` + `tax-strategist` together
- Bug report → `debugger`

## Decision authority chain

`research-analyst` proposes → `behavioral-finance-guard` validates emotional
state → `portfolio-analyst` sizes → CC executes manually. Atlas never trades.

`cashflow-monitor` flips the spend gate → `cfo.pulse.publish()` → Maven
reads cfo_pulse.json → Maven gates campaigns.

`compliance-auditor` raises a flag → `tax-strategist` plans the response →
CC files (Atlas prepares forms but never transmits).
