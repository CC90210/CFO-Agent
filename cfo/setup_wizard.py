"""
cfo/setup_wizard.py
-------------------
ATLAS Personalization Wizard — interactive setup for new users.

Walks through all 8 sections of docs/PERSONALIZATION_INTERVIEW.md and writes:
  brain/USER.md          -- complete financial profile
  .env                   -- API keys (appended/updated, never overwrites secrets)
  data/manual_balances.json  -- opening balances

Usage
-----
  python main.py setup
  python main.py setup --non-interactive   # populates demo data, no stdin required

Standalone:
  python -m cfo.setup_wizard
"""

from __future__ import annotations

import json
import shutil
import sys
from datetime import date
from pathlib import Path
from typing import Any, Callable

_ROOT = Path(__file__).resolve().parents[1]
_BRAIN = _ROOT / "brain"
_DATA = _ROOT / "data"
_ENV = _ROOT / ".env"
_ENV_EXAMPLE = _ROOT / ".env.example"

# Keys the wizard can write to .env (never touches existing secrets already set)
_API_KEY_VARS: dict[str, str] = {
    "ANTHROPIC_API_KEY":   "Anthropic API key (https://console.anthropic.com)",
    "EXCHANGE_API_KEY":    "Kraken API key (read-only balance key recommended)",
    "EXCHANGE_SECRET":     "Kraken API secret",
    "OANDA_TOKEN":         "OANDA REST API token",
    "OANDA_ACCOUNT_ID":    "OANDA account ID (e.g. 101-002-12345678-001)",
    "WISE_API_TOKEN":      "Wise API token (read-only)",
    "WISE_PROFILE_ID":     "Wise profile ID (numeric)",
    "STRIPE_API_KEY":      "Stripe restricted API key (read-only)",
    "TELEGRAM_BOT_TOKEN":  "Telegram bot token (from @BotFather)",
    "TELEGRAM_CHAT_ID":    "Telegram chat ID (your personal chat or group)",
    "GMAIL_USER":          "Gmail address for receipt scanning",
    "GMAIL_APP_PASSWORD":  "Gmail app password (NOT your regular password)",
}

# Demo data used with --non-interactive
_DEMO_DATA: dict[str, Any] = {
    "identity": {
        "name": "Demo User",
        "dob": "1995-01-15",
        "location": "Toronto, Ontario, Canada",
        "relocation_planned": "No",
        "relocation_target": "",
    },
    "citizenship": {
        "citizenship": "Canadian",
        "eligible_citizenship": "None",
        "crown_dependencies_interest": "No",
        "marital_status": "Single",
        "dependents": "None",
        "family_income_context": "N/A",
    },
    "income_business": {
        "employment_type": "Self-employed / sole proprietor (T2125)",
        "business_structure": "Sole proprietor",
        "incorporation_status": "Not incorporated",
        "income_sources": [
            {
                "name": "Consulting",
                "type": "Consulting",
                "currency": "CAD",
                "monthly": 5000,
                "concentration_pct": 60,
                "trajectory": "stable",
            }
        ],
        "mrr_total": "5000 CAD",
        "revenue_annual": "60000 CAD",
        "customer_concentration_pct": "60%",
        "payment_processors": "Direct bank deposit",
        "income_currencies": "CAD",
        "multi_currency_accounts": "No",
    },
    "accounts": {
        "primary_bank": "RBC",
        "secondary_banks": "None",
        "tfsa_status": "Yes",
        "tfsa_balance": 5000.0,
        "tfsa_room": 46000.0,
        "rrsp_status": "Yes",
        "rrsp_balance": 0.0,
        "rrsp_room": 27000.0,
        "fhsa_status": "No",
        "fhsa_balance": 0.0,
        "resp_status": "No",
        "us_accounts": "No",
        "stock_brokers": "Wealthsimple",
        "crypto_platforms": "None",
        "crypto_holdings": "None",
        "forex_platforms": "None",
        "cold_wallets": "No",
        "foreign_accounts": "No",
        "foreign_property_cost": "0",
    },
    "assets_liabilities": {
        "cash_cad": 10000.0,
        "cash_usd": 0.0,
        "investments": "TFSA: $5,000 in XEQT ETF",
        "real_estate": "No (renting)",
        "rent_monthly": 1500.0,
        "equipment": "Laptop: $1,200 (Class 50 CCA)",
        "liabilities": "None",
        "student_loan_status": "N/A",
    },
    "tax_situation": {
        "last_return_filed": "2024",
        "current_filing_status": "Not filed yet",
        "filing_method": "Wealthsimple Tax NETFILE",
        "expected_deductions": "Home office, software, subscriptions",
        "home_office_sqft_pct": "15%",
        "vehicle_business_use_pct": "0%",
        "loss_carryforwards": "None",
        "unused_credits": "None",
        "sr_ed_eligible": "Possibly, if tech qualifies",
    },
    "risk_goals": {
        "risk_tolerance": "Moderate",
        "investment_horizon": "10+ years for FIRE core; 6-18 months for active picks",
        "primary_goal": "Wealth building + tax optimization",
        "secondary_goals": "FIRE, home purchase",
        "concerns": "Income concentration, tax liability",
        "income_target": "150,000 CAD/year within 5 years",
        "time_budget": "2-3 hours/week",
    },
    "data_access": {
        "gmail_enabled": "No",
        "stripe_enabled": "No",
        "wise_enabled": "No",
        "exchange_api_enabled": "No",
        "research_api_tier": "Free tier",
        "api_keys": {},
    },
    "communication": {
        "preferred_channels": "CLI only",
        "telegram_configured": "No",
        "check_in_cadence": "Monthly",
        "alert_runway_months": 3,
        "alert_concentration_pct": 85,
        "alert_unrealized_loss_pct": 5,
        "alert_tax_days": 30,
    },
}


class SetupWizard:
    """
    Interactive personalization wizard for ATLAS.

    Walks the user through 8 sections matching PERSONALIZATION_INTERVIEW.md,
    then writes brain/USER.md, updates .env, and saves data/manual_balances.json.
    """

    def __init__(self, non_interactive: bool = False) -> None:
        self._non_interactive = non_interactive
        self._today = date.today().isoformat()

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Master orchestrator — walks all 8 sections."""
        self._banner()

        if self._non_interactive:
            self._print("Running in --non-interactive mode with demo data.")
            # Back up existing USER.md before overwriting so real data is safe
            user_md_path = _BRAIN / "USER.md"
            if user_md_path.exists():
                backup = _BRAIN / f"USER.md.backup-{self._today}"
                shutil.copy(user_md_path, backup)
                self._print(f"  Backup saved to {backup.name}")
            data = dict(_DEMO_DATA)
        else:
            # Check for existing USER.md
            self._check_existing_user_md()

            data = {
                "identity":         self._section_identity(),
                "citizenship":      self._section_citizenship(),
                "income_business":  self._section_income_business(),
                "accounts":         self._section_accounts(),
                "assets_liabilities": self._section_assets_liabilities(),
                "tax_situation":    self._section_tax_situation(),
                "risk_goals":       self._section_risk_goals(),
                "data_access":      self._section_data_access(),
                "communication":    self._section_communication(),
            }

        self._print("\n" + "=" * 60)
        self._print("  Writing files...")
        self._print("=" * 60)

        user_md = self._render_user_md(data)
        user_md_path = _BRAIN / "USER.md"
        _BRAIN.mkdir(parents=True, exist_ok=True)
        user_md_path.write_text(user_md, encoding="utf-8")
        self._print(f"  [OK] brain/USER.md written")

        self._update_env(data.get("data_access", {}))
        self._print(f"  [OK] .env updated")

        self._update_balances(data)
        self._print(f"  [OK] data/manual_balances.json written")

        self._print("\nSetup complete. Run `python main.py networth` to verify.")

    # ------------------------------------------------------------------
    # Section methods
    # ------------------------------------------------------------------

    def _section_identity(self) -> dict[str, Any]:
        self._section_header("A. Identity & Personal Information")
        name = self._prompt("Legal name (as on your ID)", default="TODO")
        dob = self._prompt("Date of birth (YYYY-MM-DD)", default="TODO")
        location = self._prompt("Current city, province/state, country",
                                default="TODO")
        relocation = self._prompt("Planning to relocate in next 12 months? (yes/no)",
                                  default="no")
        reloc_target = ""
        if relocation.lower().startswith("y"):
            reloc_target = self._prompt("Relocation target (city + timeline)",
                                        default="TODO")
        return {
            "name": name,
            "dob": dob,
            "location": location,
            "relocation_planned": relocation,
            "relocation_target": reloc_target,
        }

    def _section_citizenship(self) -> dict[str, Any]:
        self._section_header("A2/A3. Citizenship & Family")
        citizenship = self._prompt(
            "Citizenship(s) held (e.g. Canadian + British)",
            default="Canadian")
        eligible = self._prompt(
            "Other citizenships you are eligible for (or 'None')",
            default="None")
        crown = self._prompt(
            "Interested in Crown Dependencies tax planning if UK passport? (yes/no/na)",
            default="no")
        marital = self._prompt(
            "Marital status",
            choices=["Single", "Common-law", "Married", "Separated", "Divorced"],
            default="Single")
        dependents = self._prompt("Dependents (children, etc.) or 'None'",
                                  default="None")
        family_income = self._prompt(
            "Family income context (e.g. 'Mother ~$80K, Dad in Ireland') or 'N/A'",
            default="N/A")
        return {
            "citizenship": citizenship,
            "eligible_citizenship": eligible,
            "crown_dependencies_interest": crown,
            "marital_status": marital,
            "dependents": dependents,
            "family_income_context": family_income,
        }

    def _section_income_business(self) -> dict[str, Any]:
        self._section_header("B. Income & Business")
        employment = self._prompt(
            "Employment type",
            choices=[
                "Self-employed / sole proprietor (T2125)",
                "Employed full-time (T4)",
                "Employed part-time (T4)",
                "Incorporated (T2/T5)",
                "Passive income only",
                "Multiple",
            ],
            default="Self-employed / sole proprietor (T2125)")
        biz_structure = self._prompt(
            "Business structure",
            choices=["Sole proprietor", "CCPC", "Partnership", "LLC (US)", "Other"],
            default="Sole proprietor")
        inc_status = self._prompt("Incorporation status", default="Not incorporated")

        self._print("\n  Income sources (press Enter with no name to finish):")
        sources: list[dict[str, Any]] = []
        while True:
            name = self._prompt("  Source name (or Enter to finish)", default="")
            if not name:
                break
            src_type = self._prompt("  Type (SaaS / consulting / salary / freelance / trading / other)",
                                    default="consulting")
            currency = self._prompt("  Currency", default="CAD")
            monthly_str = self._prompt("  Monthly amount (numbers only)", default="0")
            try:
                monthly = float(monthly_str.replace(",", "").replace("$", ""))
            except ValueError:
                monthly = 0.0
            conc = self._prompt("  Customer concentration % from largest client", default="100")
            traj = self._prompt("  Trajectory (stable/growing/declining)", default="stable")
            sources.append({
                "name": name,
                "type": src_type,
                "currency": currency,
                "monthly": monthly,
                "concentration_pct": conc,
                "trajectory": traj,
            })
        if not sources:
            sources = [{"name": "TODO", "type": "TODO", "currency": "CAD",
                        "monthly": 0, "concentration_pct": "TODO",
                        "trajectory": "TODO"}]

        mrr = self._prompt("Total monthly recurring revenue (MRR)", default="TODO")
        revenue = self._prompt("Estimated annual revenue", default="TODO")
        conc_pct = self._prompt("Revenue concentration from largest client (%)", default="TODO")
        processors = self._prompt("Payment processors (e.g. Stripe, Wise, direct)",
                                  default="TODO")
        currencies = self._prompt("Income currencies (e.g. USD, CAD)", default="CAD")
        multi_currency = self._prompt("Multi-currency accounts? (yes/no)", default="no")
        return {
            "employment_type": employment,
            "business_structure": biz_structure,
            "incorporation_status": inc_status,
            "income_sources": sources,
            "mrr_total": mrr,
            "revenue_annual": revenue,
            "customer_concentration_pct": conc_pct,
            "payment_processors": processors,
            "income_currencies": currencies,
            "multi_currency_accounts": multi_currency,
        }

    def _section_accounts(self) -> dict[str, Any]:
        self._section_header("C. Accounts & Platforms")
        primary_bank = self._prompt("Primary bank", default="TODO")
        secondary_banks = self._prompt("Secondary banks or 'None'", default="None")
        tfsa = self._prompt("TFSA status (yes/no)", default="no")
        tfsa_bal = 0.0
        tfsa_room = 0.0
        if tfsa.lower().startswith("y"):
            tfsa_bal = float(
                self._prompt("  TFSA balance (CAD)", default="0").replace(",", ""))
            tfsa_room = float(
                self._prompt("  TFSA estimated room (CAD)", default="7000").replace(",", ""))
        rrsp = self._prompt("RRSP status (yes/no)", default="no")
        rrsp_bal = 0.0
        rrsp_room = 0.0
        if rrsp.lower().startswith("y"):
            rrsp_bal = float(
                self._prompt("  RRSP balance (CAD)", default="0").replace(",", ""))
            rrsp_room = float(
                self._prompt("  RRSP room (CAD)", default="27000").replace(",", ""))
        fhsa = self._prompt("FHSA status (yes/no)", default="no")
        fhsa_bal = 0.0
        if fhsa.lower().startswith("y"):
            fhsa_bal = float(
                self._prompt("  FHSA balance (CAD)", default="0").replace(",", ""))
        resp = self._prompt("RESP status (yes/no/na)", default="no")
        us_accts = self._prompt("US accounts (401k/IRA)? (yes/no)", default="no")
        brokers = self._prompt("Stock/ETF brokers (e.g. Wealthsimple, IBKR)",
                               default="TODO")
        crypto_plat = self._prompt("Crypto platforms (e.g. Kraken, Wealthsimple) or 'None'",
                                   default="None")
        crypto_holdings = self._prompt("Current crypto holdings summary or 'None'",
                                       default="None")
        forex_plat = self._prompt("Forex/metals platforms (e.g. OANDA) or 'None'",
                                  default="None")
        cold_wallets = self._prompt("Cold wallets (Ledger, Trezor)? (yes/no)",
                                    default="no")
        foreign_accts = self._prompt(
            "Foreign accounts/property outside Canada? (yes/no)", default="no")
        foreign_cost = "0"
        if foreign_accts.lower().startswith("y"):
            foreign_cost = self._prompt(
                "  Total cost basis of foreign assets (CAD)", default="0")
        return {
            "primary_bank": primary_bank,
            "secondary_banks": secondary_banks,
            "tfsa_status": "Yes" if tfsa.lower().startswith("y") else "No",
            "tfsa_balance": tfsa_bal,
            "tfsa_room": tfsa_room,
            "rrsp_status": "Yes" if rrsp.lower().startswith("y") else "No",
            "rrsp_balance": rrsp_bal,
            "rrsp_room": rrsp_room,
            "fhsa_status": "Yes" if fhsa.lower().startswith("y") else "No",
            "fhsa_balance": fhsa_bal,
            "resp_status": resp,
            "us_accounts": us_accts,
            "stock_brokers": brokers,
            "crypto_platforms": crypto_plat,
            "crypto_holdings": crypto_holdings,
            "forex_platforms": forex_plat,
            "cold_wallets": cold_wallets,
            "foreign_accounts": foreign_accts,
            "foreign_property_cost": foreign_cost,
        }

    def _section_assets_liabilities(self) -> dict[str, Any]:
        self._section_header("D. Assets & Liabilities")
        cash_cad_str = self._prompt("Total CAD cash (all accounts)", default="0")
        try:
            cash_cad = float(cash_cad_str.replace(",", "").replace("$", ""))
        except ValueError:
            cash_cad = 0.0
        cash_usd_str = self._prompt("USD cash (Wise, bank, etc.)", default="0")
        try:
            cash_usd = float(cash_usd_str.replace(",", "").replace("$", ""))
        except ValueError:
            cash_usd = 0.0
        investments = self._prompt(
            "Investment holdings summary (asset, platform, value) or 'None'",
            default="None")
        real_estate = self._prompt(
            "Real estate (primary/rental/none)", default="None")
        rent_str = self._prompt("Monthly rent (0 if owner)", default="0")
        try:
            rent_monthly = float(rent_str.replace(",", "").replace("$", ""))
        except ValueError:
            rent_monthly = 0.0
        equipment = self._prompt(
            "Business equipment (description + approx value) or 'None'",
            default="None")
        liabilities = self._prompt(
            "Debts (student loan, credit card, mortgage) or 'None'",
            default="None")
        student_status = self._prompt(
            "Student loan status (repaying/RAP/deferred/na)", default="na")
        return {
            "cash_cad": cash_cad,
            "cash_usd": cash_usd,
            "investments": investments,
            "real_estate": real_estate,
            "rent_monthly": rent_monthly,
            "equipment": equipment,
            "liabilities": liabilities,
            "student_loan_status": student_status,
        }

    def _section_tax_situation(self) -> dict[str, Any]:
        self._section_header("E. Tax Situation")
        last_filed = self._prompt("Last tax year filed", default="2024")
        filing_status = self._prompt(
            "Current year filing status",
            choices=["Not filed yet", "Filed, not assessed", "Assessed", "Under review"],
            default="Not filed yet")
        filing_method = self._prompt(
            "Filing method",
            choices=["Wealthsimple Tax NETFILE", "TurboTax", "StudioTax", "CPA", "Other"],
            default="Wealthsimple Tax NETFILE")
        deductions = self._prompt(
            "Expected deductions (comma-separated: home office, software, etc.)",
            default="TODO")
        home_office = self._prompt("Home office % of home dedicated to work (0 if none)",
                                   default="0")
        vehicle = self._prompt("Vehicle business use % (0 if none)", default="0")
        carryforward = self._prompt("Capital loss carryforwards from prior years or 'None'",
                                    default="None")
        credits = self._prompt("Unused tax credits or 'None'", default="None")
        sred = self._prompt("SR&ED eligible? (yes/no/maybe)", default="maybe")
        return {
            "last_return_filed": last_filed,
            "current_filing_status": filing_status,
            "filing_method": filing_method,
            "expected_deductions": deductions,
            "home_office_sqft_pct": home_office + "%",
            "vehicle_business_use_pct": vehicle + "%",
            "loss_carryforwards": carryforward,
            "unused_credits": credits,
            "sr_ed_eligible": sred,
        }

    def _section_risk_goals(self) -> dict[str, Any]:
        self._section_header("F. Risk Tolerance & Goals")
        risk = self._prompt(
            "Risk tolerance",
            choices=["Conservative", "Moderate", "Aggressive", "Speculative"],
            default="Moderate")
        horizon = self._prompt(
            "Investment horizon (e.g. '5-10 years core; 6-18 months picks')",
            default="TODO")
        primary_goal = self._prompt("Primary financial goal", default="Wealth building")
        secondary = self._prompt(
            "Secondary goals (comma-separated or multi-line)",
            default="TODO")
        concerns = self._prompt(
            "Top financial concerns (comma-separated)", default="TODO")
        income_target = self._prompt(
            "Target income level (annual, e.g. $200K CAD within 5 years)",
            default="TODO")
        time_budget = self._prompt(
            "Hours per week willing to spend on financial management",
            default="2-3")
        return {
            "risk_tolerance": risk,
            "investment_horizon": horizon,
            "primary_goal": primary_goal,
            "secondary_goals": secondary,
            "concerns": concerns,
            "income_target": income_target,
            "time_budget": time_budget,
        }

    def _section_data_access(self) -> dict[str, Any]:
        self._section_header("G. Data Access (API Keys)")
        self._print("  You can skip any key by pressing Enter. Placeholders will be")
        self._print("  added to .env with a TODO marker. Keys are NEVER stored in")
        self._print("  USER.md — only in .env.\n")

        gmail = self._prompt("Gmail receipt scanning? (yes/no)", default="no")
        stripe = self._prompt("Stripe revenue tracking? (yes/no)", default="no")
        wise = self._prompt("Wise balance tracking? (yes/no)", default="no")
        exchange = self._prompt("Exchange APIs (Kraken/OANDA)? (yes/no)", default="no")
        research_tier = self._prompt(
            "Research API tier (free/paid)", default="free")

        api_keys: dict[str, str] = {}
        if not self._non_interactive:
            platforms_to_configure: list[str] = []
            if gmail.lower().startswith("y"):
                platforms_to_configure += ["GMAIL_USER", "GMAIL_APP_PASSWORD"]
            if stripe.lower().startswith("y"):
                platforms_to_configure += ["STRIPE_API_KEY"]
            if wise.lower().startswith("y"):
                platforms_to_configure += ["WISE_API_TOKEN", "WISE_PROFILE_ID"]
            if exchange.lower().startswith("y"):
                platforms_to_configure += [
                    "EXCHANGE_API_KEY", "EXCHANGE_SECRET",
                    "OANDA_TOKEN", "OANDA_ACCOUNT_ID",
                ]
            platforms_to_configure += ["ANTHROPIC_API_KEY", "TELEGRAM_BOT_TOKEN",
                                       "TELEGRAM_CHAT_ID"]

            for var in platforms_to_configure:
                desc = _API_KEY_VARS.get(var, var)
                val = self._prompt(
                    f"  {var} -- {desc}\n  (press Enter to skip)",
                    default="")
                if val:
                    api_keys[var] = val

        return {
            "gmail_enabled": gmail,
            "stripe_enabled": stripe,
            "wise_enabled": wise,
            "exchange_api_enabled": exchange,
            "research_api_tier": research_tier,
            "api_keys": api_keys,
        }

    def _section_communication(self) -> dict[str, Any]:
        self._section_header("H. Communication Preferences")
        channels = self._prompt(
            "Preferred channels",
            choices=["CLI only", "Telegram", "Telegram + CLI", "Email", "Slack"],
            default="CLI only")
        telegram_configured = "No"
        if "telegram" in channels.lower():
            telegram_configured = self._prompt(
                "Telegram already configured in .env? (yes/no)", default="no")
        cadence = self._prompt(
            "Check-in cadence",
            choices=["Daily", "2-3x/week", "Weekly", "Monthly", "Quarterly",
                     "On-demand only"],
            default="Monthly")
        runway_months = self._prompt(
            "Alert when runway drops below X months", default="3")
        concentration = self._prompt(
            "Alert when income concentration exceeds X%", default="85")
        unrealized = self._prompt(
            "Alert when unrealized losses exceed X% of portfolio", default="5")
        tax_days = self._prompt(
            "Alert when tax deadline within X days", default="30")
        return {
            "preferred_channels": channels,
            "telegram_configured": telegram_configured,
            "check_in_cadence": cadence,
            "alert_runway_months": int(runway_months) if runway_months.isdigit() else 3,
            "alert_concentration_pct": int(concentration) if concentration.isdigit() else 85,
            "alert_unrealized_loss_pct": int(unrealized) if unrealized.isdigit() else 5,
            "alert_tax_days": int(tax_days) if tax_days.isdigit() else 30,
        }

    # ------------------------------------------------------------------
    # Writers
    # ------------------------------------------------------------------

    def _render_user_md(self, data: dict[str, Any]) -> str:
        """Generate a fresh brain/USER.md from collected section data."""
        ident = data.get("identity", {})
        cit = data.get("citizenship", {})
        inc = data.get("income_business", {})
        accts = data.get("accounts", {})
        assets = data.get("assets_liabilities", {})
        tax = data.get("tax_situation", {})
        goals = data.get("risk_goals", {})
        comms = data.get("communication", {})

        # Compute age if dob is parseable
        age_str = "TODO"
        dob_str = ident.get("dob", "")
        if dob_str and dob_str != "TODO":
            try:
                dob_parsed = date.fromisoformat(dob_str)
                today = date.today()
                age = today.year - dob_parsed.year - (
                    (today.month, today.day) < (dob_parsed.month, dob_parsed.day))
                age_str = str(age)
            except ValueError:
                age_str = "TODO"

        # Format income sources
        sources_block = ""
        for src in inc.get("income_sources", []):
            sources_block += (
                f"\n### {src.get('name', 'TODO')}\n"
                f"- Type: {src.get('type', 'TODO')}\n"
                f"- Currency: {src.get('currency', 'CAD')}\n"
                f"- Monthly: {src.get('monthly', 'TODO')}\n"
                f"- Concentration: {src.get('concentration_pct', 'TODO')}% from largest client\n"
                f"- Trajectory: {src.get('trajectory', 'TODO')}\n"
            )
        if not sources_block:
            sources_block = "\n- TODO: Add income sources\n"

        alerts = comms
        lines = [
            f"---",
            f"name: Financial Profile",
            f"description: {ident.get('name', 'TODO')} -- complete financial identity, goals, accounts, citizenship",
            f"tags: [user, profile, financial, identity]",
            f"last_updated: {self._today} (setup wizard)",
            f"---",
            f"",
            f"# {ident.get('name', 'TODO')} -- Financial Profile",
            f"",
            f"> Generated by ATLAS setup wizard on {self._today}.",
            f"> Update this file after major life or financial changes.",
            f"",
            f"## Identity",
            f"",
            f"- **Name:** {ident.get('name', 'TODO')}",
            f"- **Age:** {age_str} (born {ident.get('dob', 'TODO')})",
            f"- **Location:** {ident.get('location', 'TODO')}",
            f"- **Relocation Planned:** {ident.get('relocation_planned', 'No')}",
            f"- **Relocation Target:** {ident.get('relocation_target', 'N/A') or 'N/A'}",
            f"- **Marital Status:** {cit.get('marital_status', 'TODO')}",
            f"- **Dependents:** {cit.get('dependents', 'None')}",
            f"",
            f"## Citizenship",
            f"",
            f"- **Citizenship(s):** {cit.get('citizenship', 'TODO')}",
            f"- **Eligible For:** {cit.get('eligible_citizenship', 'None')}",
            f"- **Crown Dependencies Interest:** {cit.get('crown_dependencies_interest', 'No')}",
            f"- **Family Income Context:** {cit.get('family_income_context', 'N/A')}",
            f"",
            f"## Employment & Business",
            f"",
            f"- **Employment Type:** {inc.get('employment_type', 'TODO')}",
            f"- **Business Structure:** {inc.get('business_structure', 'TODO')}",
            f"- **Incorporation Status:** {inc.get('incorporation_status', 'TODO')}",
            f"- **Payment Processors:** {inc.get('payment_processors', 'TODO')}",
            f"- **Income Currencies:** {inc.get('income_currencies', 'CAD')}",
            f"- **Multi-Currency Accounts:** {inc.get('multi_currency_accounts', 'No')}",
            f"",
            f"## Revenue",
            f"",
            f"- **MRR Total:** {inc.get('mrr_total', 'TODO')}",
            f"- **Annual Revenue:** {inc.get('revenue_annual', 'TODO')}",
            f"- **Customer Concentration:** {inc.get('customer_concentration_pct', 'TODO')}",
            f"",
            f"### Income Sources",
            sources_block,
            f"## Banking & Accounts",
            f"",
            f"- **Primary Bank:** {accts.get('primary_bank', 'TODO')}",
            f"- **Secondary Banks:** {accts.get('secondary_banks', 'None')}",
            f"",
            f"### Registered Accounts",
            f"",
            f"- **TFSA:** {accts.get('tfsa_status', 'No')} | Balance: ${accts.get('tfsa_balance', 0):,.2f} CAD | Room: ${accts.get('tfsa_room', 0):,.2f} CAD",
            f"- **RRSP:** {accts.get('rrsp_status', 'No')} | Balance: ${accts.get('rrsp_balance', 0):,.2f} CAD | Room: ${accts.get('rrsp_room', 0):,.2f} CAD",
            f"- **FHSA:** {accts.get('fhsa_status', 'No')} | Balance: ${accts.get('fhsa_balance', 0):,.2f} CAD",
            f"- **RESP:** {accts.get('resp_status', 'No')}",
            f"- **US Accounts (401k/IRA):** {accts.get('us_accounts', 'No')}",
            f"",
            f"### Trading Accounts",
            f"",
            f"- **Stock Brokers:** {accts.get('stock_brokers', 'TODO')}",
            f"- **Crypto Platforms:** {accts.get('crypto_platforms', 'None')}",
            f"- **Crypto Holdings:** {accts.get('crypto_holdings', 'None')}",
            f"- **Forex/Metals Platforms:** {accts.get('forex_platforms', 'None')}",
            f"- **Cold Wallets:** {accts.get('cold_wallets', 'No')}",
            f"- **Foreign Accounts:** {accts.get('foreign_accounts', 'No')}",
            f"- **Foreign Property Cost Basis:** ${accts.get('foreign_property_cost', '0')} CAD",
            f"",
            f"## Assets & Liabilities",
            f"",
            f"- **Cash (CAD):** ${assets.get('cash_cad', 0):,.2f}",
            f"- **Cash (USD):** ${assets.get('cash_usd', 0):,.2f}",
            f"- **Monthly Rent:** ${assets.get('rent_monthly', 0):,.2f} CAD",
            f"- **Investments:** {assets.get('investments', 'None')}",
            f"- **Real Estate:** {assets.get('real_estate', 'None')}",
            f"- **Equipment:** {assets.get('equipment', 'None')}",
            f"- **Liabilities:** {assets.get('liabilities', 'None')}",
            f"- **Student Loan Status:** {assets.get('student_loan_status', 'N/A')}",
            f"",
            f"## Tax Situation",
            f"",
            f"- **Last Return Filed:** {tax.get('last_return_filed', 'TODO')}",
            f"- **Current Filing Status:** {tax.get('current_filing_status', 'TODO')}",
            f"- **Filing Method:** {tax.get('filing_method', 'TODO')}",
            f"- **Expected Deductions:** {tax.get('expected_deductions', 'TODO')}",
            f"- **Home Office %:** {tax.get('home_office_sqft_pct', '0%')}",
            f"- **Vehicle Business Use %:** {tax.get('vehicle_business_use_pct', '0%')}",
            f"- **Capital Loss Carryforwards:** {tax.get('loss_carryforwards', 'None')}",
            f"- **Unused Tax Credits:** {tax.get('unused_credits', 'None')}",
            f"- **SR&ED Eligible:** {tax.get('sr_ed_eligible', 'Unknown')}",
            f"",
            f"## Risk Tolerance & Goals",
            f"",
            f"- **Risk Tolerance:** {goals.get('risk_tolerance', 'TODO')}",
            f"- **Investment Horizon:** {goals.get('investment_horizon', 'TODO')}",
            f"- **Primary Goal:** {goals.get('primary_goal', 'TODO')}",
            f"- **Secondary Goals:** {goals.get('secondary_goals', 'TODO')}",
            f"- **Primary Concerns:** {goals.get('concerns', 'TODO')}",
            f"- **Income Target:** {goals.get('income_target', 'TODO')}",
            f"- **Time Budget:** {goals.get('time_budget', '2-3')} hours/week",
            f"",
            f"## Communication Preferences",
            f"",
            f"- **Preferred Channels:** {comms.get('preferred_channels', 'CLI only')}",
            f"- **Telegram Configured:** {comms.get('telegram_configured', 'No')}",
            f"- **Check-in Cadence:** {comms.get('check_in_cadence', 'Monthly')}",
            f"",
            f"### Alert Thresholds",
            f"",
            f"- Runway drops below **{alerts.get('alert_runway_months', 3)} months**",
            f"- Income concentration exceeds **{alerts.get('alert_concentration_pct', 85)}%**",
            f"- Unrealized losses exceed **{alerts.get('alert_unrealized_loss_pct', 5)}%**",
            f"- Tax deadline within **{alerts.get('alert_tax_days', 30)} days**",
            f"",
            f"## Data Access",
            f"",
            f"- **Gmail Receipt Scanning:** {data.get('data_access', {}).get('gmail_enabled', 'No')}",
            f"- **Stripe Revenue Tracking:** {data.get('data_access', {}).get('stripe_enabled', 'No')}",
            f"- **Wise Balance Tracking:** {data.get('data_access', {}).get('wise_enabled', 'No')}",
            f"- **Exchange API (Kraken/OANDA):** {data.get('data_access', {}).get('exchange_api_enabled', 'No')}",
            f"- **Research API Tier:** {data.get('data_access', {}).get('research_api_tier', 'Free')}",
            f"- **API Keys:** Stored in .env (never in this file)",
            f"",
            f"---",
            f"*Generated by `python main.py setup` on {self._today}. Edit this file to update.*",
        ]
        return "\n".join(lines) + "\n"

    def _update_env(self, data_access: dict[str, Any]) -> None:
        """
        Append/update .env with entered API keys.
        Never overwrites an already-set non-empty value.
        Starts from .env.example if .env does not exist.
        """
        if not _ENV.exists() and _ENV_EXAMPLE.exists():
            shutil.copy(_ENV_EXAMPLE, _ENV)

        # Read existing .env content
        existing_lines: list[str] = []
        if _ENV.exists():
            existing_lines = _ENV.read_text(encoding="utf-8").splitlines()

        # Parse existing keys
        existing_keys: dict[str, str] = {}
        for line in existing_lines:
            stripped = line.strip()
            if stripped.startswith("#") or "=" not in stripped:
                continue
            key, _, val = stripped.partition("=")
            existing_keys[key.strip()] = val.strip()

        api_keys: dict[str, str] = data_access.get("api_keys", {})

        # Figure out what to add/update
        additions: list[str] = []
        for var, val in api_keys.items():
            current = existing_keys.get(var, "")
            if current and current not in ("", "your_exchange_api_key_here",
                                           "your_telegram_bot_token", "sk-ant-..."):
                # Already configured — don't touch
                continue
            if val:
                additions.append(f"{var}={val}")
                existing_keys[var] = val

        # For any wizard-relevant vars not yet in .env, add TODO placeholders
        todo_vars = [
            v for v in _API_KEY_VARS
            if v not in existing_keys or not existing_keys[v]
        ]
        todo_additions = [f"# TODO: {v}=" for v in todo_vars if v not in {
            k.split("=")[0] for k in additions}]

        if additions or todo_additions:
            with _ENV.open("a", encoding="utf-8") as fh:
                fh.write("\n# ── Added by setup wizard " + self._today + " ──\n")
                for line in additions:
                    fh.write(line + "\n")
                if todo_additions:
                    fh.write("# Keys still needed (fill in manually):\n")
                    for line in todo_additions:
                        fh.write(line + "\n")

    def _update_balances(self, data: dict[str, Any]) -> None:
        """Write data/manual_balances.json from assets + accounts section."""
        _DATA.mkdir(parents=True, exist_ok=True)

        assets = data.get("assets_liabilities", {})
        accts = data.get("accounts", {})

        balances: list[dict[str, Any]] = []

        cash_cad = assets.get("cash_cad", 0.0)
        if cash_cad > 0:
            balances.append({
                "platform": accts.get("primary_bank", "Bank"),
                "account": "Checking",
                "amount": cash_cad,
                "currency": "CAD",
                "category": "cash",
                "notes": "set during setup wizard",
            })

        cash_usd = assets.get("cash_usd", 0.0)
        if cash_usd > 0:
            balances.append({
                "platform": "Wise",
                "account": "USD",
                "amount": cash_usd,
                "currency": "USD",
                "category": "cash",
                "notes": "set during setup wizard",
            })

        tfsa_bal = accts.get("tfsa_balance", 0.0)
        if accts.get("tfsa_status", "No").lower().startswith("y") and tfsa_bal >= 0:
            balances.append({
                "platform": "Wealthsimple",
                "account": "TFSA",
                "amount": tfsa_bal,
                "currency": "CAD",
                "category": "registered",
                "notes": "",
            })

        rrsp_bal = accts.get("rrsp_balance", 0.0)
        if accts.get("rrsp_status", "No").lower().startswith("y"):
            balances.append({
                "platform": "Wealthsimple",
                "account": "RRSP",
                "amount": rrsp_bal,
                "currency": "CAD",
                "category": "registered",
                "notes": "",
            })

        fhsa_bal = accts.get("fhsa_balance", 0.0)
        if accts.get("fhsa_status", "No").lower().startswith("y"):
            balances.append({
                "platform": "Wealthsimple",
                "account": "FHSA",
                "amount": fhsa_bal,
                "currency": "CAD",
                "category": "registered",
                "notes": f"opened {self._today}",
            })

        if not balances:
            balances.append({
                "platform": "Manual",
                "account": "Default",
                "amount": 0.0,
                "currency": "CAD",
                "category": "cash",
                "notes": "update this file with real balances",
            })

        payload = {
            "as_of": self._today,
            "balances": balances,
        }

        out_path = _DATA / "manual_balances.json"
        with out_path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _prompt(
        self,
        question: str,
        default: str | None = None,
        validator: Callable[[str], bool] | None = None,
        choices: list[str] | None = None,
    ) -> str:
        """
        Show a prompt and return the user's answer (or default on empty input).
        Handles Ctrl+C gracefully by returning the default or empty string.
        In --non-interactive mode always returns the default.
        """
        if self._non_interactive:
            return default or ""

        prompt_parts = [f"  {question}"]
        if choices:
            for i, c in enumerate(choices, 1):
                prompt_parts.append(f"    [{i}] {c}")
        if default is not None:
            prompt_parts.append(f"  [default: {default}] > ")
        else:
            prompt_parts.append("  > ")

        prompt_str = "\n".join(prompt_parts)

        while True:
            try:
                raw = input(prompt_str).strip()
            except (KeyboardInterrupt, EOFError):
                self._print("\n  (skipped)")
                return default or ""

            # Numeric shortcut for choices
            if choices and raw.isdigit():
                idx = int(raw) - 1
                if 0 <= idx < len(choices):
                    return choices[idx]

            if not raw:
                if default is not None:
                    return default
                self._print("  (using empty value)")
                return ""

            if validator and not validator(raw):
                self._print("  Invalid input. Try again.")
                continue

            return raw

    def _check_existing_user_md(self) -> None:
        """If USER.md already exists, prompt for overwrite and offer backup."""
        user_md_path = _BRAIN / "USER.md"
        if not user_md_path.exists():
            return
        try:
            ans = input(
                "\n  brain/USER.md already exists. Overwrite? (yes/no/backup) "
                "[default: backup] > "
            ).strip().lower()
        except (KeyboardInterrupt, EOFError):
            ans = "backup"

        if ans in ("", "backup", "b"):
            backup = _BRAIN / f"USER.md.backup-{self._today}"
            shutil.copy(user_md_path, backup)
            self._print(f"  Backup saved to {backup.name}")
        elif ans in ("no", "n"):
            self._print("  Aborting setup to preserve existing USER.md.")
            sys.exit(0)
        # "yes" falls through — file will be overwritten

    def _banner(self) -> None:
        self._print("=" * 60)
        self._print("  ATLAS Setup Wizard")
        self._print("  Personalization Interview -- approx 10-15 minutes")
        self._print("  Press Enter to accept defaults | Ctrl+C to skip a question")
        self._print("=" * 60 + "\n")

    def _section_header(self, title: str) -> None:
        self._print(f"\n{'─' * 60}")
        self._print(f"  {title}")
        self._print(f"{'─' * 60}")

    @staticmethod
    def _print(msg: str) -> None:
        """Write to stdout. Centralised so it can be silenced in tests."""
        sys.stdout.write(msg + "\n")
        sys.stdout.flush()


# ---------------------------------------------------------------------------
# CLI entry (python -m cfo.setup_wizard)
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(
        prog="setup_wizard",
        description="ATLAS personalization wizard — writes brain/USER.md, .env, and manual_balances.json",
    )
    ap.add_argument(
        "--non-interactive", action="store_true",
        help="Populate with demo data without reading from stdin (for testing)",
    )
    args = ap.parse_args()
    SetupWizard(non_interactive=args.non_interactive).run()


if __name__ == "__main__":
    main()
