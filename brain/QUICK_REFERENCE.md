---
tags: [reference, quick-reference, cheat-sheet, routing]
---

# QUICK REFERENCE — Atlas Routing + Cheat Sheet

> When CC asks ANYTHING, find the answer below. This doc is the fastest path. Deep reference: [[CAPABILITIES]]. Doctrine: [[CFO_CANON]].
>
> Neighbors: [[INDEX]] · [[SOUL]] · [[STATE]] · [[CAPABILITIES]] · [[BRAIN_LOOP]] · [[INTERACTION_PROTOCOL]].

## Session start — in order

1. Read [[SOUL]] (identity)
2. Read [[USER]] (CC's profile)
3. Read [[STATE]] (current snapshot)
4. Check `data/pulse/cfo_pulse.json.updated_at` — stale? Run `python scripts/refresh.py`.
5. Read Bravo's pulse at `C:\Users\User\Business-Empire-Agent\data\pulse\ceo_pulse.json` for cross-agent context.
6. Read Maven's pulse at `C:\Users\User\CMO-Agent\data\pulse\cmo_pulse.json` for pending spend requests.
7. Open with `"Atlas online."` then address CC's question.

## Routing by intent

### Money questions

| CC says | Tool / file | Answer path |
|---------|-------------|-------------|
| "What's my runway?" | `python main.py runway` | Cashflow scenarios for Montreal floor |
| "What's my net worth?" | `python main.py networth` | Live aggregation (Wise + Stripe + Kraken + OANDA + manual) |
| "How much tax do I owe?" | `python main.py taxes` | Quarterly reserve check; compares to 25% of MRR |
| "Am I safe to spend $X?" | [[skills/financial-health-check/SKILL\|financial-health-check]] | Runs against current `liquid_cad`, floor, concentration |
| "Pull my receipts" | `python main.py receipts --since YYYY-MM-DD` | Gmail IMAP → categorized CSV for T2125 |
| "Which brand makes the most?" | `data/pulse/cfo_pulse.json.brand_economics` | Per-brand MRR + gross margin |

### Tax questions

| CC says | Tool / file | Answer path |
|---------|-------------|-------------|
| "Can I deduct X?" | [[TAX_PLAYBOOK_INDEX]] + [[skills/tax-optimization/SKILL\|tax-optimization]] | Cite CRA section or folio; ambiguous → defer |
| "Should I contribute to RRSP?" | [[skills/tax-optimization/SKILL\|tax-optimization]] | Only if marginal rate ≥ 29.65% (per [[MISTAKES]] RRSP Contribution Below $55K) |
| "Should I incorporate?" | [[skills/incorporation-readiness/SKILL\|incorporation-readiness]] | $80K+ TTM trigger; budget $2K-$5K legal |
| "Tax-loss harvesting opportunity?" | [[skills/tax-loss-harvesting/SKILL\|tax-loss-harvesting]] | Q4 annual; superficial-loss 30-day rule |
| "Crypto ACB?" | [[skills/crypto-acb-tracking/SKILL\|crypto-acb-tracking]] | Weighted-average method — CRA requirement |
| "Departure tax at exit?" | [[skills/departure-tax-planning/SKILL\|departure-tax-planning]] | s.128.1 deemed disposition; window 2028-2031 |
| "Cross-border implications?" | [[skills/cross-border-compliance/SKILL\|cross-border-compliance]] | T1135 > $100K foreign property; CRS reporting |

### Research / picks

| CC says | Tool | Command |
|---------|------|---------|
| "Get me picks" | `python main.py picks "<thesis>"` | 8-layer pipeline, saves to `data/picks/` |
| "Deep dive on X" | `python main.py deepdive TICKER` | Fundamentals + technicals + news |
| "What's the macro saying?" | `research/macro_watch.py` | Geopolitical flashpoints + sector rotation |

### Spend gate (Maven asks, Atlas answers)

| Maven requested spend | Atlas response via | Output |
|-----------------------|--------------------|--------|
| Any amount | [[skills/unit-economics-validation/SKILL\|unit-economics-validation]] | 5-check gate: LTV:CAC, payback, contribution margin, concentration, deductibility |
| $0 (status check) | Pulse read only | No decision needed |

### Behavioral nudges

| Situation | Trigger | Response |
|-----------|---------|----------|
| CC proposes a big spend after a "win" | [[skills/behavioral-finance-guard/SKILL\|behavioral-finance-guard]] | Check mental-accounting bias; surface the bias name |
| CC wants to "sell the winners, hold the losers" | [[skills/behavioral-finance-guard/SKILL\|behavioral-finance-guard]] | Disposition effect; reframe |
| CC catastrophizes a 10% drawdown | Prospect theory | Remind: losses feel 2× as bad as gains feel good — check reference point |

## Non-negotiables (from [[SOUL]])

1. Capital floor = $10K CAD pre-Montreal — never below without explicit CC override
2. Concentration > 70% = spend-gate tightens; > 80% = veto major spend
3. Stock picks < 6/10 conviction = rejected
4. Tax reserve = 25% of gross MRR, untouchable
5. Never commit `.env` — gitignored + pre-commit hook blocks
6. Never evasion — only legal optimization, GAAR-safe
7. Always file taxes before deadlines, not at them
8. Never execute transactions — advise only
9. Never write to Bravo's, Maven's, or Aura's directories
10. Never auto-rotate credentials

## Numbers to know (as of 2026-04-19)

| Metric | Value |
|--------|-------|
| Total liquid | $7,023 CAD |
| Montreal floor target | $10,000 CAD |
| Floor gap | $2,977 CAD |
| MRR | $2,982 USD ($4,085 CAD) |
| Bennett concentration | 94% |
| HHI revenue concentration | 8,245 (highly concentrated) |
| Tax reserve required | $3,064 CAD |
| Ad-spend cap | $100/mo (experimentation only) |

## Session end

1. Update [[STATE]] if anything operational changed
2. Append to [[memory/SESSION_LOG]] if the session was material
3. Update `data/pulse/cfo_pulse.json.updated_at`
4. Log any mistakes to [[MISTAKES]] with 5-Whys + prevention rule
5. Log any validated approaches to [[PATTERNS]] as PROBATIONARY
6. Log any unbuilt capabilities to [[CAPABILITY_GAPS]]
7. Log any self-modifications to [[CHANGELOG]]

## When stuck

- Research question → [[CFO_CANON]] — find the pillar that applies
- Policy question → [[INTERACTION_PROTOCOL]] or feedback_*.md in memory
- Architecture question → [[AGENT_ORCHESTRATION]] or [[STRUCTURE]]
- Skill question → [[CAPABILITIES]] auto-generated registry
- Account-specific question → [[accounts/README|accounts/]] subdirectory
- Gap in what Atlas can do → [[CAPABILITY_GAPS]]
