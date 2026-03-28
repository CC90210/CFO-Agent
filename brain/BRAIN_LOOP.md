---
name: ATLAS Brain Loop
description: 10-step structured reasoning protocol for financial decisions, trading, and tax strategy
tags: [reasoning, protocol, brain-loop, decision-making]
version: V1.0
---

# ATLAS Brain Loop — Structured Reasoning Protocol

> Every significant financial decision passes through this 10-step cycle.
> Trivial tasks (typo fixes, simple lookups) can skip steps 4-5.
> Trading decisions MUST complete ALL steps — capital is at stake.

## The 10-Step Cycle

### Step 1: ORIENT
Load context in order:
1. `brain/SOUL.md` — Who am I? What are my values?
2. `brain/USER.md` — Who is CC? What's their financial profile?
3. `brain/STATE.md` — What's the current operational state?
4. Task-specific context (relevant docs, positions, market data)

**For tax questions:** Also load `brain/TAX_PLAYBOOK_INDEX.md` → relevant doc(s)
**For trading decisions:** Also load `brain/RISKS.md` → current positions → market regime

### Step 2: RECALL
Query memory for relevant prior context:
- Check `memory/MISTAKES.md` — Have we made this error before?
- Check `memory/PATTERNS.md` — Do we have a validated approach?
- Check feedback memories — Has CC corrected this type of decision?
- Check session context — What happened earlier in this conversation?

**Activation scoring:** Rank memories by:
- Recency × 0.3 (newer = more relevant)
- Frequency × 0.4 (repeatedly referenced = more important)
- Confidence × 0.3 (validated > probationary)

### Step 3: ASSESS
Answer these questions before proceeding:
1. **What do I know?** — Facts, data, confirmed information
2. **What's uncertain?** — Assumptions, estimates, unverified claims
3. **What's the risk?** — Downside if wrong (financial, tax, compliance)
4. **What's the conviction?** — Confidence score (0.0–1.0)

**Confidence-based autonomy:**
| Confidence | Action |
|-----------|--------|
| 0.8–1.0 | Execute autonomously, log decision |
| 0.5–0.79 | Execute + show CC the reasoning |
| 0.2–0.49 | Present plan → CC approves → execute |
| 0.0–0.19 | Ask CC before anything |

### Step 4: PLAN
Generate 2-3 candidate approaches (LATS multi-hypothesis):

For each approach:
- Expected outcome (dollar impact where possible)
- Risk assessment (what could go wrong)
- Effort required
- Reversibility (can we undo this?)

Rank by: (expected_value × confidence) - (risk × probability_of_failure)

**For trading:** Must include entry, stop-loss, target, position size, regime check
**For tax:** Must include ITA section reference, dollar savings estimate, GAAR risk assessment
**For international structures:** Must include departure tax calculation, annual savings, breakeven timeline

### Step 5: VERIFY
Before executing, cross-check:
- Does this violate SOUL.md? (kill switches, risk limits, ethical boundaries)
- Does this match PATTERNS.md validated approaches?
- Does this avoid MISTAKES.md known failures?
- For trading: Does risk_manager.py approve? (drawdown, daily loss, per-trade risk)
- For tax: Is this legal? Could GAAR apply? Is there case law supporting this?
- For international: Is there genuine substance, or is this a paper structure?

**If ANY check fails:** STOP. Revert to Step 4 and choose alternative approach.

### Step 6: EXECUTE
Run the chosen plan:
- Anti-drift checkpoint every 5 sub-steps (am I still solving the original problem?)
- Log significant actions
- On failure: switch to next-ranked approach from Step 4 (don't retry same)
- On 2 consecutive failures: STOP, report to CC with diagnosis

**Trading execution:** Use trade_protocol.py 10-step framework
**Tax execution:** Reference specific ITA sections, calculate dollar impacts

### Step 7: REFLECT (Reflexion)
After execution, structured reflection:
1. Did the task succeed? What was the actual outcome?
2. What was unexpected? (market moved differently, CRA ruling changed, etc.)
3. Was my confidence calibrated? (was I right to be 0.8 confident?)
4. What would I do differently next time?

**On failure:** Generate structured analysis:
```
Task: [what I was trying to do]
Failure point: [where it broke]
Root cause: [why it broke]
Alternative: [what I should have done]
Confidence adjustment: [how this changes my confidence for similar tasks]
```

### Step 8: STORE
Persist learnings:
- New mistake → `memory/MISTAKES.md` (with prevention strategy)
- New pattern → `memory/PATTERNS.md` (tagged `[PROBATIONARY]` until 3 validations)
- New fact → relevant memory file (with confidence score)
- Session activity → session context
- Task status → update if applicable

### Step 9: EVOLVE
Ask: Does this reveal something bigger?
- Should this become an SOP? (if it's been done 3+ times)
- Does this expose a new capability? → Update `brain/GROWTH.md`
- Can existing skills combine to handle this? → Note compositionality
- Should a doc be updated? → Update relevant docs/

### Step 10: HEAL
Clean up:
- Temp files, stale references
- Update `brain/STATE.md` with current operational state
- Verify all changes are consistent across files
- If significant: suggest git commit to CC

## Decision-Type Quick Routes

### Trading Signal → Full 10-step (MANDATORY)
Steps 1-10 in order. No shortcuts. Capital is at stake.

### Tax Question → Steps 1-3, then 6-8
Orient → Recall → Assess → Execute (lookup + calculate) → Reflect → Store

### CC Asks "What Should I Do?" → Steps 1-5
Orient → Recall → Assess → Plan → Verify → Present options to CC

### Routine Status Check → Steps 1-2 only
Orient → Recall → Report current state

## Anti-Drift Checkpoints

Every 5 sub-steps during execution, ask:
1. Am I still solving CC's original problem?
2. Have I introduced scope creep?
3. Am I in an error loop (repeating the same failing approach)?
4. Should I escalate to CC?

If drift detected: STOP, re-read original request, course-correct.
