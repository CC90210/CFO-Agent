---
tags: [brands, portfolio, registry, cfo]
---

# BRANDS — Portfolio Brand Registry

> Atlas's view of every revenue-producing brand CC operates. Mirrors Bravo's CLIENT_PLAYBOOK pattern, scoped for CFO concerns: gross margin, concentration, tax treatment, and spend governance.
>
> Authoritative machine-readable form: `data/pulse/cfo_pulse.json.brand_economics`. This doc is the human-readable companion + context each brand needs that doesn't fit JSON.
>
> Neighbors: [[INDEX]] · [[STATE]] · [[USER]] · [[CFO_CANON]] · [[skills/unit-economics-validation/SKILL|unit-economics-validation]] · [[accounts/README|accounts/]].

## Portfolio summary (2026-04-19)

| Brand | Status | MRR (CAD) | GM% | Share of MRR | HHI contribution |
|-------|--------|----------:|----:|-------------:|-----------------:|
| Bennett | active — concentration risk | $3,425 | 70% | 90.7% | 8,226 |
| OASIS | active — primary product | $242 | 85% | 6.4% | 41 |
| Nostalgic | side income | $108 | 90% | 2.9% | 8 |
| PropFlow | pre-revenue | $0 | 80% (placeholder) | 0% | 0 |
| SunBiz | dormant planned | $0 | — | 0% | 0 |
| **Total** | | **$3,775** | weighted 73% | 100% | **8,275** |

HHI = Σ (share² × 10,000). > 2,500 = highly concentrated per US DOJ antitrust threshold. Target < 2,500 before ad-spend cap loosens.

---

## Bennett (Skool partnership)

**Status:** active — largest revenue line, concentration villain
**Revenue model:** $2,500 USD flat monthly retainer + 15% rev-share on Skool community sales
**Payment path:** Wise payment link (USD) → Atlas's `WISE_PROFILE_ID` → CAD conversion on withdrawal
**Gross margin:** ~70% (INFERRED from CC's ~15-20 hrs/mo opportunity cost; no formal time tracking)
**Contract:** month-to-month, no minimums, no lock-in
**Retention risk:** HIGH — single point of failure for 90%+ of CC's income
**CFO directives:**
- Concentration flag active in every [[STATE]] brief until < 70%
- Every dollar of Bennett revenue goes through standard 25% tax-reserve first
- CC should NOT raise prices on Bennett mid-contract — churn risk outweighs the upside at current concentration
- Bravo (CEO) owns the diversification push; Atlas's job is to keep runway safe while that plays out
**Tax treatment:** USD income recognized in CAD at spot rate on receipt date (CRA s.261); sole-prop line 8000 until incorporation, then corporate revenue

## OASIS AI Solutions

**Status:** active — primary productized offering
**Revenue model:** SaaS subscriptions + implementation + consulting
**Payment path:** Stripe (USD payouts to Wise) + direct Wise transfers for consulting
**Gross margin:** ~85% (API + hosting = ~$298/mo burn against $242 CAD MRR — margin currently inverted at this scale, normalizes as MRR grows)
**Contract:** Stripe subscriptions, no minimums, cancel-anytime
**Retention risk:** N/A yet — only 2 paid subscribers beyond Bennett
**CFO directives:**
- Most scalable brand; priority for reinvestment once liquid > floor
- Atlas is OASIS's own flagship implementation — eat own dogfood, publicly visible code is marketing
- Business-in-a-Box product ships under OASIS brand
- Tax treatment: SaaS revenue line 8000; qualifies for SR&ED credits on genuine R&D (needs log — see [[TAX_PLAYBOOK_INDEX]] § SR&ED)
**Unit economics (when ready):**
- Validate against [[skills/unit-economics-validation/SKILL|unit-economics-validation]] before any OASIS ad campaign
- Target LTV:CAC ≥ 3 per David Skok ([[CFO_CANON]] Knowledge Frontier)
- Target CAC payback ≤ 12 months

## Nostalgic (DJ / music)

**Status:** side income — stable low-volume
**Revenue model:** DJ gigs (13 in 2025 = $1,300 CAD) + potential Stripe side-income channel
**Payment path:** mixed — cash, e-transfer, occasional Stripe
**Gross margin:** ~90% (Serato $21/mo + SoundCloud $10/mo = ~$31 COGS; equipment amortizes via CCA Class 50)
**Retention risk:** LOW — not a growth lever; seasonal & volunteer
**CFO directives:**
- Not a growth target; do NOT fund Maven ads against this brand
- Tax-optimize what exists: deduct Serato + SoundCloud + equipment CCA + travel to gigs (T2125 line 8710) + meal allowance per CRA meal-and-entertainment rules (50%)
- DJ income is self-employment (T2125), NOT hobby income — document receipts + gig dates

## PropFlow

**Status:** pre-revenue — building phase
**Revenue model:** SaaS (planned)
**Payment path:** Stripe (when live)
**Gross margin:** 80% (PLACEHOLDER — assumes OASIS-like SaaS pattern; overwrite with real data)
**Retention risk:** Cannot assess — no cohort
**CFO directives:**
- No ad spend approved. Need at least 3 paying customers before [[skills/unit-economics-validation/SKILL|unit-economics-validation]] can even run.
- Dev costs are deductible (hosting, API, contractor fees if any); capture in monthly Gmail receipt sweep
- Track hours for potential SR&ED credit if work is genuinely novel R&D

## SunBiz

**Status:** dormant — planned but not active
**Revenue model:** TBD
**CFO directives:**
- Not tracked operationally. Activates when Bravo greenlights.
- Placeholder kept so brand_economics schema is portfolio-complete; remove if CC deprecates the concept.

---

## Portfolio-level rules

### Concentration management (enforced via [[skills/unit-economics-validation/SKILL|unit-economics-validation]])

| Concentration (single client % of MRR) | Atlas response |
|---|---|
| < 50% | Normal — standard spend gate applies |
| 50-70% | Watch — concentration called out in every [[STATE]] brief |
| 70-80% | Spend-gate multiplier × 0.5 |
| ≥ 80% | Discretionary spend veto (major ad campaigns, major equipment, non-essential subscriptions) |
| ≥ 90% (current) | Active veto + weekly diversification standup with Bravo |

### Gross-margin hurdle

Any brand with sustained gross margin < 40% is flagged for a strategic review. Either the pricing is wrong, the COGS structure is wrong, or the brand shouldn't be a priority brand. GM < 20% is a kill recommendation unless Atlas has a named reason (loss leader, strategic positioning) backed by [[CFO_CANON]] Porter Five Forces.

### Tax-efficient brand sequencing

Once CCPC lands (mid-2026 at $80K TTM):
1. OASIS → CCPC (SaaS + services; qualifies for small-business deduction at 12.2% Ontario)
2. Nostalgic → stays sole-prop T2125 (side income, not worth corp overhead)
3. PropFlow → CCPC if revenue materializes, otherwise retired
4. SunBiz → decide at activation

Bennett (the client, not a CC brand) pays whichever entity CC directs — post-CCPC, payments go to the corp.

---

## Maintenance rules

1. **Update when a brand launches, rebrands, or deprecates.** Not a live-tracking document for MRR (that's the pulse).
2. **Keep CFO-scoped.** If it's content voice or funnel, that's Maven. If it's sales process or client relationship, that's Bravo. Atlas tracks the money and the structure.
3. **One section per brand — don't split.** If a brand gets complex enough to need a file, create `brain/brands/<brand>.md` and link from here.
4. **INFERRED vs PLACEHOLDER labels match the pulse.** When a placeholder fills with real data, update both simultaneously.
