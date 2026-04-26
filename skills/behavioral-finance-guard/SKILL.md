---
name: behavioral-finance-guard
version: 0.1.0
status: PROBATIONARY
description: "Catches behavioral biases in the operator's financial decisions BEFORE Atlas endorses them. Runs a 9-bias checklist on every money decision the operator proposes (buy, sell, spend, contribute, withdraw). Returns the bias name, the formal source, and a reframe. The point is not to overrule the operator — it is to make sure the operator knows which bias they are fighting."
metadata:
  category: behavioral-oversight
  owner: atlas
  consumers: [operator-decision-flow, pre-approval-of-spend, pre-pick-sizing]
  tier: full
triggers: [check-bias, behavioral-review, loss-aversion-check, anchoring-check, sunk-cost-check, mental-accounting-check, overconfidence-check, disposition-effect-check, recency-bias-check, herding-check, framing-check]
sources:
  - "Kahneman & Tversky — Prospect Theory (1979) — loss aversion, probability weighting, reference dependence"
  - "Kahneman — Thinking, Fast and Slow (2011) — System 1 / System 2, anchoring, availability heuristic"
  - "Thaler — Mental Accounting (1985), Nudge (2008) — mental buckets, status quo bias, choice architecture"
  - "Munger — The Psychology of Human Misjudgment (2005) — 25 biases compounded"
  - "Shefrin & Statman — Disposition Effect (1985) — selling winners, holding losers"
  - "Cialdini — Influence (1984) — social proof, commitment, scarcity effects"
  - "Housel — The Psychology of Money (2020) — behavioral explanations in accessible form"
---

# behavioral-finance-guard — The CFO's bias checklist

> Atlas's job is to protect the operator's capital. The biggest threat is usually not markets — it is the operator's own brain. This skill runs a 9-bias scan on every meaningful money decision BEFORE Atlas endorses it.
>
> Neighbors: [[CFO_CANON]] § Kahneman / Thaler / Munger · [[PATTERNS]] · [[MISTAKES]] · [[QUICK_REFERENCE]] · [[INDEX]].

## When to invoke

**Automatic** whenever:
1. Operator proposes a spend > $250 that isn't a recurring committed expense
2. Operator proposes a stock pick sell DURING a position that shows a gain or loss > 20%
3. Operator considers a BUY within 48h of a dramatic market move (up or down > 5%)
4. Operator asks about tax-loss harvesting within 30 days of another harvest (superficial loss zone)
5. Operator expresses emotion-laden language: "I'm sick of this", "I have to get in on this", "I'll make it back", "everyone is doing this"
6. A pending Maven ad-spend request is ≥ 50% of approved monthly cap

**Manual**: operator asks "am I being rational here?" or "check my reasoning"

## The 9 biases this skill scans for

### 1. Loss aversion (Kahneman-Tversky)
**The pattern**: losses feel ~2× as bad as equivalent gains feel good. Operator refuses to sell a loser because realizing the loss "makes it real." Or conversely, sells a winner too early to "lock in" the gain.
**Detection signal**: language like "I'll get back to break-even first." Or: "I want to lock this in before it goes back down."
**Reframe**: "Would you buy this position today at the current price? If no, the decision to hold is identical to the decision to buy — you're implicitly buying every day you don't sell."
**Source**: [[CFO_CANON]] § Kahneman-Tversky Prospect Theory

### 2. Mental accounting (Thaler)
**The pattern**: money gets treated differently by its source. Bonus money, tax refund, windfall → "play money" (spent frivolously). Salary → "serious money" (saved carefully).
**Detection signal**: "It's just the tax refund — doesn't really count." "I'll spend the Bennett 15% bonus on something fun."
**Reframe**: "A dollar is a dollar regardless of source. Apply the standard allocation rule (save/invest/spend %) to ALL incoming dollars, not just the predictable ones."
**Source**: [[CFO_CANON]] § Thaler Mental Accounting

### 3. Anchoring (Kahneman)
**The pattern**: fixating on an irrelevant reference point. "I bought at $100, so I won't sell below $100 even though fair value is $60." "The original price was $2,000 so $1,500 is a deal" — even if $1,500 is still above real value.
**Detection signal**: decisions framed around purchase price, last-seen price, headline price rather than current fundamentals.
**Reframe**: "Ignore what you paid. What is this worth today? What would you pay for it today if you didn't already own it?"
**Source**: [[CFO_CANON]] § Kahneman Thinking Fast and Slow

### 4. Sunk-cost fallacy (Kahneman, Thaler)
**The pattern**: continuing to invest in a losing position because of what's already been spent. "I've already put $5K into this — I can't quit now."
**Detection signal**: "If I sell now I'll have wasted the time I spent researching" / "I'm already down $2K, might as well ride it out."
**Reframe**: "Past costs are gone either way. The only question is: given what I know now, what is the best use of the NEXT dollar and the NEXT hour? Would I start this position today from scratch?"
**Source**: [[CFO_CANON]] § Kahneman

### 5. Disposition effect (Shefrin-Statman)
**The pattern**: sell winners, hold losers — the opposite of what tax-efficient investing requires. Driven by loss aversion + mental accounting.
**Detection signal**: operator proposing to sell a gainer + hold a loser when a risk-based review would suggest the opposite.
**Reframe**: "A tax-aware investor prefers to sell losers (realize the tax loss — offsetting gains elsewhere) and hold winners (defer the tax event into a lower-bracket jurisdiction). Your instinct here is backwards from the tax-aware play."
**Source**: [[CFO_CANON]] § Shefrin-Statman (next-tier)

### 6. Overconfidence (Kahneman, Munger)
**The pattern**: operator believes their information edge is larger than it is. Leads to oversized positions, undersized research, underestimated downside.
**Detection signal**: proposed position size > 10% of liquid, or pick justification that skips the bear case, or language like "I know this one, trust me."
**Reframe**: "If you're right, what's the upside?  If you're wrong, what's the downside? Do the ratio. Then halve your conviction and re-run."
**Source**: [[CFO_CANON]] § Munger Psychology of Human Misjudgment

### 7. Recency bias (Kahneman)
**The pattern**: overweighting recent events. A hot stock becomes "clearly a winner" after 3 up days. A 10% drop becomes "the start of the crash."
**Detection signal**: operator proposing a decision based on very-recent market action with no cycle context. Or: "This keeps going up, I have to get in."
**Reframe**: "Zoom out. Where does this sit in the 5-year chart? In the cycle? What was the narrative 6 months ago? Is the news itself more extreme than the underlying change?"
**Source**: [[CFO_CANON]] § Kahneman + Marks second-level thinking

### 8. Herding / social proof (Cialdini)
**The pattern**: decisions driven by what others are doing rather than independent analysis. Especially bad at market extremes.
**Detection signal**: "Everyone on [Twitter/Reddit/Discord] is talking about this." "Hormozi said..." "All my friends are in."
**Reframe**: "Social proof is a signal — of popularity, not correctness. What is your independent thesis, and is it better or worse than the consensus thesis the crowd is operating on?"
**Source**: [[CFO_CANON]] § Cialdini (next-tier)

### 9. Framing effect (Kahneman-Tversky)
**The pattern**: same decision, different outcomes depending on how it's presented. "90% survival rate" vs "10% mortality rate" — identical information, different decisions.
**Detection signal**: language like "I could save $X" (gain frame) when the operator actually has to SPEND $Y to get that. Or: "avoid losing $X" when the realistic outcome is merely slower compounding.
**Reframe**: "Restate the decision in neutral terms: given my current state, does this action increase or decrease expected wealth — and by how much vs the alternative use of the same capital/time?"
**Source**: [[CFO_CANON]] § Kahneman-Tversky Prospect Theory

## Output format

Atlas emits into its pulse or its decision trace:

```json
"behavioral_check": {
  "decision": "Sell BTC in Wealthsimple Crypto to fund Maven Meta ads",
  "biases_detected": [
    {
      "name": "mental_accounting",
      "evidence": "Operator framed BTC as 'not really my money' vs RBC checking which is 'real' money",
      "reframe": "Both are capital. Dispose only if disposition is the best use of THAT capital. Realizing BTC loss for ad spend locks in loss AND commits capital to a channel whose unit economics haven't cleared [[skills/unit-economics-validation/SKILL|unit-economics-validation]].",
      "source": "Thaler 1985"
    },
    {
      "name": "sunk_cost_fallacy",
      "evidence": "Operator cited 'I already built the campaign infrastructure' as reason to spend",
      "reframe": "Infra spend is sunk. Only question is: is the NEXT dollar of spend positive contribution margin? Per unit-economics-validation Check 3: FAIL (close rate is forecast not historical).",
      "source": "Kahneman 2011"
    }
  ],
  "recommendation": "HOLD. Operator's reasoning contains 2 detected biases. Reframed above. If operator still wishes to proceed after reading the reframes, proceed — but log the override.",
  "bias_override_logged": false
}
```

## Rules

1. **Never overrule the operator**. Surface the bias, provide the reframe. The operator decides.
2. **If an override is chosen, log it in [[memory/PATTERNS]] or [[memory/MISTAKES]]** depending on outcome. Three overrides of the same bias → that bias is probably not a bias for this operator.
3. **Don't over-fire**. Not every decision needs a 9-bias scan. Use the WHEN-TO-INVOKE triggers; over-firing turns the skill into noise.
4. **Frame reframes as questions, not lectures**. "Would you buy this today?" is a reframe. "You shouldn't sell" is a lecture. Lectures get ignored.
5. **Pair with hard rules where relevant**. A position > 80% concentration is VETOED by [[skills/unit-economics-validation/SKILL|unit-economics-validation]] regardless of bias-check. Behavioral guard doesn't override SOUL non-negotiables.

## Anti-patterns (what this skill is NOT)

1. **Not a therapist.** Atlas doesn't diagnose the operator's psychology broadly. Scope is limited to money decisions.
2. **Not a gotcha tool.** Every operator has biases — including Atlas. The frame is "here's what this bias pattern looks like," not "you are irrational."
3. **Not a replacement for skill-level logic.** Unit-economics-validation, tax-loss-harvesting, etc. do the quantitative work. This skill is the behavioral overlay, not the primary gate.

## Metrics for success

| Metric | Target | Review cadence |
|--------|--------|----------------|
| Bias-firing accuracy | ≥ 70% of fires surface a bias the operator agrees is present | Monthly |
| Decision-change rate | 30-60% of fires result in the operator changing the decision (too high = over-firing; too low = under-firing) | Monthly |
| False-positive rate | ≤ 15% of fires are "this isn't actually bias, the decision is correct" | Monthly |
| Time-to-decision increase | < 5 minutes added per check | Per-fire |

If metrics trip below target for two consecutive reviews, trigger Protocol 4 Reflexion on this skill.

## Promotion to [VALIDATED]

After 3 fires where:
- The bias was real (operator agreed retrospectively)
- The reframe changed the decision
- The changed decision produced a better outcome (6-month retrospective on reversed sells; 3-month on reversed spends)

Log outcomes in [[memory/PATTERNS]].

## Cross-references

- [[CFO_CANON]] — the canonical behavioral-finance sources (Kahneman, Thaler, Munger, Cialdini, Housel)
- [[skills/unit-economics-validation/SKILL|unit-economics-validation]] — pairs with spend decisions
- [[skills/position-sizing/SKILL|position-sizing]] — pairs with overconfidence check (sizing as a conviction check)
- [[skills/tax-loss-harvesting/SKILL|tax-loss-harvesting]] — pairs with disposition-effect check
- [[MISTAKES]] — historical bias-driven mistakes
- [[PATTERNS]] — overrides logged here when operator pushes through a surfaced bias
