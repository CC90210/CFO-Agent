"""
config/settings.py
------------------
Central settings management for Atlas Trading Agent.

All values are loaded from environment variables (via .env) and
validated at startup using pydantic-settings. Hard-coded defaults
are deliberately conservative — they can be overridden in .env.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root — one level above this file
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class RiskSettings(BaseSettings):
    """Risk-management parameters."""

    model_config = SettingsConfigDict(env_file=str(PROJECT_ROOT / ".env"), extra="ignore")

    max_drawdown_pct: float = Field(
        default=15.0,
        ge=1.0,
        le=50.0,
        description="Stop trading when total drawdown from equity peak exceeds this percentage.",
    )
    daily_loss_limit_pct: float = Field(
        default=5.0,
        ge=0.5,
        le=20.0,
        description="Stop trading for the rest of the day when intraday loss exceeds this percentage.",
    )
    per_trade_risk_pct: float = Field(
        default=1.5,
        ge=0.1,
        le=10.0,
        description="Percentage of total equity risked on each individual trade.",
    )
    max_open_positions: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Maximum number of simultaneous open positions.",
    )


class ExchangeSettings(BaseSettings):
    """Exchange connectivity settings."""

    model_config = SettingsConfigDict(env_file=str(PROJECT_ROOT / ".env"), extra="ignore")

    default_exchange: str = Field(
        default="binance",
        description="CCXT exchange id (e.g. 'binance', 'okx', 'bybit').",
    )
    exchange_api_key: str = Field(default="", description="Exchange API key.")
    exchange_secret: str = Field(default="", description="Exchange API secret.")
    exchange_passphrase: str = Field(
        default="",
        description="Passphrase for exchanges that require it (OKX, KuCoin).",
    )
    paper_trade: bool = Field(
        default=True,
        description="When True, orders are simulated and never sent to the exchange.",
    )
    confirm_live: bool = Field(
        default=False,
        description="Explicit opt-in required before live orders are placed.",
    )

    @model_validator(mode="after")
    def live_requires_confirmation(self) -> "ExchangeSettings":
        """Prevent accidental live trading without the explicit flag."""
        if not self.paper_trade and not self.confirm_live:
            raise ValueError(
                "Live trading requires CONFIRM_LIVE=true in your .env file. "
                "Set PAPER_TRADE=false AND CONFIRM_LIVE=true to enable live orders."
            )
        return self


class TelegramSettings(BaseSettings):
    """Telegram notification settings."""

    model_config = SettingsConfigDict(env_file=str(PROJECT_ROOT / ".env"), extra="ignore")

    telegram_bot_token: str = Field(default="", description="Telegram bot token.")
    telegram_chat_id: str = Field(
        default="",
        description="Chat ID where trade notifications are sent.",
    )

    @property
    def enabled(self) -> bool:
        """Return True only when both token and chat ID are configured."""
        return bool(self.telegram_bot_token and self.telegram_chat_id)


class DatabaseSettings(BaseSettings):
    """Database connection settings."""

    model_config = SettingsConfigDict(env_file=str(PROJECT_ROOT / ".env"), extra="ignore")

    database_url: str = Field(
        default="sqlite:///trading_agent.db",
        description="SQLAlchemy-compatible database URL.",
    )


class AISettings(BaseSettings):
    """Anthropic / Claude settings."""

    model_config = SettingsConfigDict(env_file=str(PROJECT_ROOT / ".env"), extra="ignore")

    anthropic_api_key: str = Field(default="", description="Anthropic API key.")
    claude_model: str = Field(
        default="claude-opus-4-5",
        description="Claude model to use for agent analysis.",
    )
    max_tokens: int = Field(
        default=4096,
        ge=256,
        le=8096,
        description="Maximum tokens per Claude API call.",
    )


class LoggingSettings(BaseSettings):
    """Logging configuration."""

    model_config = SettingsConfigDict(env_file=str(PROJECT_ROOT / ".env"), extra="ignore")

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Root logger level.",
    )
    log_dir: Path = Field(
        default=PROJECT_ROOT / "logs",
        description="Directory where rotating log files are written.",
    )

    @field_validator("log_dir", mode="before")
    @classmethod
    def resolve_log_dir(cls, v: str | Path) -> Path:
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return path


class FinanceSettings(BaseSettings):
    """
    Financial planning and tax settings for CC.

    Override via .env using the FINANCE__ prefix (due to env_nested_delimiter="__"):
    e.g. FINANCE__TAX_PROVINCE=ON
    """

    model_config = SettingsConfigDict(env_file=str(PROJECT_ROOT / ".env"), extra="ignore")

    tax_province: str = Field(
        default="ON",
        description="Canadian province for provincial tax calculations (ON = Ontario).",
    )
    tax_year: int = Field(
        default=2026,
        description="Current or target tax year for calculations.",
    )
    tfsa_contribution_room: float = Field(
        default=7000.0,
        ge=0.0,
        description="Available TFSA contribution room in CAD (2024+ = $7,000/year).",
    )
    rrsp_contribution_room: float = Field(
        default=0.0,
        ge=0.0,
        description="Available RRSP deduction limit in CAD. Update from your CRA My Account.",
    )
    fhsa_contribution_room: float = Field(
        default=8000.0,
        ge=0.0,
        description="Available FHSA contribution room in CAD ($8,000/year).",
    )
    risk_tolerance: str = Field(
        default="MODERATE",
        description="Default risk tolerance: CONSERVATIVE | MODERATE | AGGRESSIVE.",
    )
    monthly_savings_target: float = Field(
        default=500.0,
        ge=0.0,
        description="Monthly savings/investment target in CAD.",
    )
    fire_target_annual_expenses: float = Field(
        default=40000.0,
        ge=0.0,
        description="Estimated annual expenses for FIRE calculation (CAD).",
    )
    fire_withdrawal_rate: float = Field(
        default=0.04,
        ge=0.01,
        le=0.10,
        description="Safe withdrawal rate for FIRE calculation (default 4% — Trinity Study).",
    )
    monthly_income: float = Field(
        default=2191.0,
        ge=0.0,
        description="CC's current MRR / monthly income in CAD. Update as revenue grows.",
    )

    @field_validator("risk_tolerance")
    @classmethod
    def validate_risk_tolerance(cls, v: str) -> str:
        allowed = {"CONSERVATIVE", "MODERATE", "AGGRESSIVE"}
        if v.upper() not in allowed:
            raise ValueError(f"risk_tolerance must be one of {allowed}, got '{v}'")
        return v.upper()

    @field_validator("tax_province")
    @classmethod
    def validate_province(cls, v: str) -> str:
        """Warn if province is not Ontario (only ON brackets are implemented)."""
        if v.upper() != "ON":
            import warnings
            warnings.warn(
                f"Tax province '{v}' is set but only Ontario (ON) brackets are "
                "implemented. Tax calculations will use Ontario rates.",
                stacklevel=2,
            )
        return v.upper()


class Settings(BaseSettings):
    """
    Top-level settings object — the single source of truth for all
    runtime configuration. Compose the domain-specific sub-settings
    so callers import one object: ``from config.settings import settings``.
    """

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_nested_delimiter="__",
        extra="ignore",
    )

    # Sub-settings (populated from the same .env file)
    risk: RiskSettings = Field(default_factory=RiskSettings)
    exchange: ExchangeSettings = Field(default_factory=ExchangeSettings)
    telegram: TelegramSettings = Field(default_factory=TelegramSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    ai: AISettings = Field(default_factory=AISettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    finance: FinanceSettings = Field(default_factory=FinanceSettings)

    # ── Convenience pass-throughs ─────────────────────────────────────────
    @property
    def is_paper(self) -> bool:
        """True when paper-trading mode is active."""
        return self.exchange.paper_trade

    @property
    def is_live(self) -> bool:
        """True only when paper_trade=False and confirm_live=True."""
        return not self.exchange.paper_trade and self.exchange.confirm_live


# Module-level singleton — import this in all other modules.
settings = Settings()
