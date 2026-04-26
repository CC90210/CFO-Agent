---
name: ATLAS Patterns
description: Validated and probationary approaches — proven methods and emerging best practices
tags: [patterns, validated, probationary, best-practices]
---

# ATLAS Patterns

> [VALIDATED] = proven in 3+ sessions. Trust these.
> [PROBATIONARY] = 1-2 observations. Promising but needs more evidence.
> [UNDER_REVIEW] = caused issues. Investigate before using again.
>
> Neighbors: [[MISTAKES]] · [[CAPABILITY_GAPS]] · [[CFO_CANON]] · [[skills/self-improvement-protocol/SKILL|self-improvement-protocol]] · [[INDEX]].

---

## CFO-Era Patterns (added 2026-04-19 via self-improvement cycle 1)

Four probationary patterns from the CFO pivot. Promote to `[VALIDATED]` after 3 successful re-uses on distinct occasions.

### [PROBATIONARY] 2026-04-19 — Pulse-gated cross-agent handshake
**Situation**: Two sovereign agents (Atlas as CFO, Maven as CMO) coordinate a shared action (ad spend) without either writing to the other's repo.
**Approach**: Atlas publishes `approved_ad_spend_monthly_cap_cad` in its own pulse. Maven reads before any campaign. Atlas writes decision into its OWN pulse. Maven writes request into its OWN pulse. Neither mutates the other. Contract: [[AGENT_ORCHESTRATION]].
**Outcome**: 3-way pulse stress test at 15/15 PASS (2026-04-18 post-reorg). Clean audit trail.
**Why it worked**: sovereignty enforced by architecture, not discipline.
**When to apply**: any cross-agent decision where authority lives with one agent and execution with another.
**Counter-indications**: pulses are eventually-consistent, not real-time. Don't use for sub-second coordination.

### [PROBATIONARY] 2026-04-19 — Canon-backed decisions over ad-hoc opinion
**Situation**: Any financial recommendation from Atlas — stock pick, tax move, spend approval, allocation shift.
**Approach**: Every recommendation names the canonical framework it derives from, with a pillar number from [[CFO_CANON]]. "Reject this spend: fails Graham's margin of safety (LTV:CAC 1.8 below 3.0) and Taleb's concentration-at-ruin check (94% single client)."
**Outcome**: [[skills/unit-economics-validation/SKILL|unit-economics-validation]] built with five named pillars. [[CFO_CANON]] established the 10-pillar canon.
**Why it worked**: forces diagnostic rigor in place of execution velocity. Makes recommendations reviewable.
**When to apply**: every recommendation, every time. If no pillar applies, the recommendation is research not advice.
**Counter-indications**: don't over-cite. One or two pillars per recommendation is signal; five is padding.

### [PROBATIONARY] 2026-04-19 — Brand-level economics over aggregate MRR
**Situation**: Portfolio has multiple revenue streams (OASIS, Bennett, SunBiz, PropFlow, Nostalgic). Aggregate MRR hides distributional risk.
**Approach**: Extended `cfo_pulse.json` with `brand_economics` — per-brand MRR, gross margin (with INFERRED vs PLACEHOLDER labels), retention, notes. Added `portfolio_summary.hhi_concentration_index`.
**Outcome**: HHI reads 8,245 — quantitatively "highly concentrated" (DOJ threshold 2,500). The qualitative "94% Bennett" becomes a number that moves.
**Why it worked**: qualitative risk is debatable; quantitative risk is not.
**When to apply**: anytime aggregates hide distributional problems — concentration, churn-by-cohort, margin-by-channel.
**Counter-indications**: INFERRED beats no number but loses to tracked number. Don't let the inferred sit forever.

### [PROBATIONARY] 2026-04-19 — "Skin in the game" self-check before advising
**Situation**: Before surfacing any recommendation, Atlas asks: "would I put my own capital into this at this size, today?"
**Approach**: Final pre-output check added to every recommendation pipeline (stock picks, spend approvals, tax strategies). If the answer is no, downgrade conviction, downsize, or withhold. Traces to [[CFO_CANON]] pillar 10.
**Outcome (expected)**: fewer hedged "could be good could be bad" recommendations.
**Why it worked (expected)**: Taleb's ethics principle applied. An advisor who wouldn't take their own advice is selling noise.
**When to apply**: every recommendation, especially where operator capital is at risk and Atlas has no skin in the outcome.
**Counter-indications**: risk of anchoring to Atlas's implicit preferences rather than the operator's objectives.

---

## Archive — Trading-Era Patterns

> Retained as reference. The trading stack was archived 2026-04-14. Some patterns (Read Before Edit, Single Daemon Instance) generalize beyond trading and stay load-bearing.

## Trading Patterns

### [VALIDATED] Regime-Aware Strategy Filtering
Regime detector classifies market as BULL/BEAR/CHOPPY/HIGH_VOL. Each strategy has per-regime weight multipliers. Backtests WITH regime filtering consistently outperform backtests without.
**Evidence:** Sessions 8, 10, 12, 15 — every strategy improved with regime awareness.

### [VALIDATED] Regime Hysteresis (min_hold_bars=6)
Don't flip regime classification on every bar. Use minimum 6-bar hold period. Reduces false regime transitions by 51%.
**Evidence:** Sessions 14, 16, 18.

### [VALIDATED] Volume as Conviction Modifier, Not Hard Gate
Volume filters should modify conviction scores, not block trades entirely. Hard volume gates killed too many valid signals.
**Evidence:** Sessions 12, 14, 17.

### [VALIDATED] Per-Strategy Trailing Stop Tuning
Trend-followers need wide stops (3x+ ATR). Mean reversion needs tight stops (1.5-2x ATR). One-size-fits-all kills either trend or reversion returns.
**Evidence:** Sessions 10, 12, 15, 18.

### [VALIDATED] /USD Suffix for Ontario Crypto
USDT restricted in Ontario. All Kraken pairs must use /USD suffix.
**Evidence:** Sessions 6, 8, 11.

### [VALIDATED] Single Daemon Instance
Only one trading daemon at a time. PID file check on startup. Multiple daemons create duplicate orders.
**Evidence:** Sessions 18, 19.

### [VALIDATED] Async CCXT — Always Await
CCXT async methods must use `await`, never `asyncio.to_thread()`. Multiple bugs traced to this.
**Evidence:** Sessions 17, 18.

### [VALIDATED] OANDA Semaphore(2)
Max 2 concurrent OANDA API calls. oandapyV20 requests.Session is not thread-safe.
**Evidence:** Sessions 18, 19.

### [VALIDATED] Portfolio Tightening > Portfolio Expansion
Removing losing strategies/pairs (+110% improvement) is more valuable than adding new ones.
**Evidence:** Sessions 15, 17.

### [PROBATIONARY] Gold Outperforms Forex
OANDA gold (XAU_USD) validates across multiple strategies. Forex majors all negative.
**Evidence:** Sessions 17, 18. Needs more data.

### [PROBATIONARY] Donchian on Gold — Best Performer
Donchian trend-following on XAU_USD: +10.93% backtest, Monte Carlo 0% ruin probability.
**Evidence:** Session 17. Single backtest — needs live validation.

### [PROBATIONARY] London Breakout on GBP_USD — 67% Win Rate
London session breakout strategy on GBP_USD shows 67% win rate in backtest.
**Evidence:** Session 18. Single backtest.

## Tax Patterns

### [VALIDATED] FHSA > TFSA > RRSP Priority Order
For CC at current income: FHSA first (deduction + tax-free growth + tax-free withdrawal), TFSA second (tax-free growth), RRSP third (only when marginal rate >= 29.65%).
**Evidence:** Sessions 20, 21, 22. Consistent across all analysis.

### [VALIDATED] Deduct NOW, Not Later
Business deductions are worth more NOW (save tax + invest the savings) even if marginal rate is lower. Time value of the tax savings outweighs waiting for a higher bracket.
**Evidence:** Sessions 21, 22.

### [VALIDATED] Crypto ACB — Weighted Average Only
CRA requires weighted-average method for crypto ACB. Not FIFO, not LIFO, not specific identification (despite some tools offering these). Weighted average across ALL wallets and exchanges.
**Evidence:** Sessions 13, 20, 22.

### [PROBATIONARY] Start SR&ED Tracking Before Incorporation
T661 claims are based on when R&D occurred, not when entity existed. Track R&D hours and activities NOW for potential retroactive claim post-incorporation.
**Evidence:** Session 23 (income scaling playbook analysis).

### [PROBATIONARY] Irish Passport as Free Option
Apply for Irish citizenship via Foreign Births Registry (€278, 6-12 months). Zero downside, unlocks EU + 6.25% KDB rate if ever needed.
**Evidence:** Session 23 (Crown Dependencies analysis).

### [PROBATIONARY] Departure Tax Window — Act While Assets Are Small
Departure tax (s.128.1) is based on FMV at time of departure. CC's current asset base is minimal (~$0 departure tax). Window closes as OASIS and crypto appreciate.
**Evidence:** Session 23 (single analysis).

## System Patterns

### [VALIDATED] Windows Daemon Launch
Use subprocess.Popen with DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP flags. nohup/disown doesn't work on Windows.
**Evidence:** Sessions 18, 19.

### [VALIDATED] Read Before Edit
Always read files before editing. Never guess at method signatures, class structures, or file contents.
**Evidence:** Multiple sessions — core development principle.

### [VALIDATED] Backtest -> Paper Trade -> Live
Never skip the pipeline. Strategies must prove themselves at each stage before promotion.
**Evidence:** Core principle, validated across all strategy deployments.
