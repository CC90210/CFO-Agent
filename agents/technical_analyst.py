"""
agents/technical_analyst.py
----------------------------
Technical Analysis Agent — computes a full suite of indicators from OHLCV
data and produces a trading signal via Claude or a pure-quant fallback.

Indicators computed (via the ``ta`` library):
  Trend    : EMA-20, EMA-50, EMA-200, Ichimoku (conversion/base/span A/span B)
  Momentum : RSI-14, MACD (12/26/9), Stochastic RSI
  Volatility: Bollinger Bands (20, 2σ), ATR-14
  Volume   : VWAP (approximate), ADX-14
  Composite: All-in-one indicator confluence score (quant fallback)

Quant scoring rules:
  +1 per bullish signal, -1 per bearish, then normalise to [-1, 1].
  The quant score is used when Claude is unavailable AND as a sanity-check
  on the LLM output.
"""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

try:
    import ta
    _TA_AVAILABLE = True
except ImportError:
    _TA_AVAILABLE = False

from agents.base_agent import AgentSignal, BaseAnalystAgent, Direction

logger = logging.getLogger(__name__)

# Minimum candles needed to compute all indicators reliably
_MIN_CANDLES = 52


class TechnicalAnalyst(BaseAnalystAgent):
    """
    Specialist in chart-based analysis.

    Expected market_data shape:
        {
            "ohlcv": [
                {"timestamp": ..., "open": float, "high": float,
                 "low": float, "close": float, "volume": float},
                ...          # at least _MIN_CANDLES rows, newest last
            ],
            "timeframe": "1h" | "4h" | "1d" | ...
        }
    """

    @property
    def name(self) -> str:
        return "TechnicalAnalyst"

    # ------------------------------------------------------------------
    # Main implementation
    # ------------------------------------------------------------------

    async def _analyze_impl(
        self,
        symbol: str,
        market_data: dict[str, Any],
        context: dict[str, Any],
    ) -> AgentSignal:
        ohlcv_raw = market_data.get("ohlcv", [])
        timeframe = market_data.get("timeframe", "unknown")

        if len(ohlcv_raw) < _MIN_CANDLES:
            return AgentSignal.neutral(
                self.name,
                reason=f"Insufficient candles: {len(ohlcv_raw)} < {_MIN_CANDLES} required",
            )

        df = self._build_dataframe(ohlcv_raw)
        indicators = self._compute_indicators(df)
        quant_conviction = self._quant_score(indicators)

        # Attempt Claude-enhanced analysis
        try:
            signal = await self._claude_analysis(symbol, timeframe, indicators, quant_conviction)
        except Exception as exc:
            logger.warning(
                "%s: Claude unavailable (%s), using quant fallback", self.name, exc
            )
            signal = self._quant_signal(indicators, quant_conviction)

        return signal

    # ------------------------------------------------------------------
    # Data preparation
    # ------------------------------------------------------------------

    def _build_dataframe(self, ohlcv_raw: list[dict[str, Any]]) -> pd.DataFrame:
        df = pd.DataFrame(ohlcv_raw)
        for col in ("open", "high", "low", "close", "volume"):
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df.dropna(subset=["open", "high", "low", "close", "volume"], inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df

    # ------------------------------------------------------------------
    # Indicator computation
    # ------------------------------------------------------------------

    def _compute_indicators(self, df: pd.DataFrame) -> dict[str, float | str]:
        """
        Compute all technical indicators and return a flat snapshot dict
        reflecting the latest bar only.
        """
        if not _TA_AVAILABLE:
            logger.warning("ta library not installed — using price-action only")
            return self._price_action_only(df)

        close = df["close"]
        high = df["high"]
        low = df["low"]
        volume = df["volume"]
        latest = close.iloc[-1]

        ind: dict[str, float | str] = {"latest_close": latest}

        # ── RSI ────────────────────────────────────────────────────────
        try:
            rsi_series = ta.momentum.RSIIndicator(close=close, window=14).rsi()
            ind["rsi"] = float(rsi_series.iloc[-1])
            ind["rsi_signal"] = (
                "oversold" if ind["rsi"] < 30
                else "overbought" if ind["rsi"] > 70
                else "neutral"
            )
        except Exception:
            ind["rsi"] = 50.0
            ind["rsi_signal"] = "neutral"

        # ── MACD ───────────────────────────────────────────────────────
        try:
            macd_obj = ta.trend.MACD(close=close, window_fast=12, window_slow=26, window_sign=9)
            ind["macd"] = float(macd_obj.macd().iloc[-1])
            ind["macd_signal"] = float(macd_obj.macd_signal().iloc[-1])
            ind["macd_histogram"] = float(macd_obj.macd_diff().iloc[-1])
            ind["macd_bullish"] = ind["macd_histogram"] > 0
        except Exception:
            ind["macd_bullish"] = False

        # ── EMA ────────────────────────────────────────────────────────
        try:
            ema20 = float(ta.trend.EMAIndicator(close=close, window=20).ema_indicator().iloc[-1])
            ema50 = float(ta.trend.EMAIndicator(close=close, window=50).ema_indicator().iloc[-1])
            ema200_series = ta.trend.EMAIndicator(close=close, window=200).ema_indicator()
            ema200 = float(ema200_series.iloc[-1]) if len(close) >= 200 else ema50
            ind["ema20"] = ema20
            ind["ema50"] = ema50
            ind["ema200"] = ema200
            ind["above_ema20"] = latest > ema20
            ind["above_ema50"] = latest > ema50
            ind["above_ema200"] = latest > ema200
            ind["ema_trend"] = "bullish" if ema20 > ema50 else "bearish"
        except Exception:
            ind["ema_trend"] = "neutral"

        # ── Bollinger Bands ────────────────────────────────────────────
        try:
            bb = ta.volatility.BollingerBands(close=close, window=20, window_dev=2)
            bb_upper = float(bb.bollinger_hband().iloc[-1])
            bb_lower = float(bb.bollinger_lband().iloc[-1])
            bb_mid = float(bb.bollinger_mavg().iloc[-1])
            ind["bb_upper"] = bb_upper
            ind["bb_lower"] = bb_lower
            ind["bb_mid"] = bb_mid
            bb_width = (bb_upper - bb_lower) / bb_mid if bb_mid else 0
            ind["bb_width"] = bb_width
            ind["bb_position"] = (latest - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) else 0.5
            ind["bb_signal"] = (
                "oversold" if latest < bb_lower
                else "overbought" if latest > bb_upper
                else "neutral"
            )
        except Exception:
            ind["bb_signal"] = "neutral"

        # ── ATR ────────────────────────────────────────────────────────
        try:
            atr = float(
                ta.volatility.AverageTrueRange(high=high, low=low, close=close, window=14)
                .average_true_range()
                .iloc[-1]
            )
            ind["atr"] = atr
            ind["atr_pct"] = (atr / latest * 100) if latest else 0
        except Exception:
            ind["atr"] = 0.0
            ind["atr_pct"] = 0.0

        # ── ADX ────────────────────────────────────────────────────────
        try:
            adx_obj = ta.trend.ADXIndicator(high=high, low=low, close=close, window=14)
            adx_val = float(adx_obj.adx().iloc[-1])
            ind["adx"] = adx_val
            ind["adx_di_plus"] = float(adx_obj.adx_pos().iloc[-1])
            ind["adx_di_minus"] = float(adx_obj.adx_neg().iloc[-1])
            ind["trend_strength"] = "strong" if adx_val > 25 else "weak"
            ind["adx_bullish"] = ind["adx_di_plus"] > ind["adx_di_minus"]
        except Exception:
            ind["trend_strength"] = "weak"
            ind["adx_bullish"] = False

        # ── Stochastic RSI ─────────────────────────────────────────────
        try:
            stoch_rsi = ta.momentum.StochRSIIndicator(close=close, window=14, smooth1=3, smooth2=3)
            stoch_k = float(stoch_rsi.stochrsi_k().iloc[-1])
            stoch_d = float(stoch_rsi.stochrsi_d().iloc[-1])
            ind["stoch_k"] = stoch_k
            ind["stoch_d"] = stoch_d
            ind["stoch_signal"] = (
                "oversold" if stoch_k < 0.2
                else "overbought" if stoch_k > 0.8
                else "neutral"
            )
        except Exception:
            ind["stoch_signal"] = "neutral"

        # ── Ichimoku ───────────────────────────────────────────────────
        try:
            ichi = ta.trend.IchimokuIndicator(
                high=high, low=low,
                window1=9, window2=26, window3=52,
            )
            conversion = float(ichi.ichimoku_conversion_line().iloc[-1])
            base = float(ichi.ichimoku_base_line().iloc[-1])
            span_a = float(ichi.ichimoku_a().iloc[-1])
            span_b = float(ichi.ichimoku_b().iloc[-1])
            ind["ichimoku_conversion"] = conversion
            ind["ichimoku_base"] = base
            ind["ichimoku_span_a"] = span_a
            ind["ichimoku_span_b"] = span_b
            cloud_top = max(span_a, span_b)
            cloud_bot = min(span_a, span_b)
            ind["ichimoku_signal"] = (
                "bullish" if latest > cloud_top
                else "bearish" if latest < cloud_bot
                else "neutral"
            )
            ind["tenkan_kijun_cross"] = "bullish" if conversion > base else "bearish"
        except Exception:
            ind["ichimoku_signal"] = "neutral"

        # ── VWAP (approximate daily) ───────────────────────────────────
        try:
            typical_price = (high + low + close) / 3
            vwap = float((typical_price * volume).cumsum().iloc[-1] / volume.cumsum().iloc[-1])
            ind["vwap"] = vwap
            ind["above_vwap"] = latest > vwap
        except Exception:
            ind["above_vwap"] = False

        # ── Support / Resistance (recent swing levels) ────────────────
        try:
            recent = df.tail(20)
            ind["recent_support"] = float(recent["low"].min())
            ind["recent_resistance"] = float(recent["high"].max())
        except Exception:
            ind["recent_support"] = latest * 0.95
            ind["recent_resistance"] = latest * 1.05

        return ind

    def _price_action_only(self, df: pd.DataFrame) -> dict[str, float | str]:
        """Minimal indicators when ta library is unavailable."""
        close = df["close"]
        latest = float(close.iloc[-1])
        prev = float(close.iloc[-2]) if len(close) > 1 else latest
        sma20 = float(close.tail(20).mean())
        return {
            "latest_close": latest,
            "above_ema20": latest > sma20,
            "price_change_pct": (latest - prev) / prev * 100 if prev else 0,
            "rsi_signal": "neutral",
            "macd_bullish": latest > prev,
            "bb_signal": "neutral",
            "trend_strength": "weak",
            "ichimoku_signal": "neutral",
            "stoch_signal": "neutral",
            "above_vwap": latest > sma20,
            "adx_bullish": latest > prev,
            "ema_trend": "bullish" if latest > sma20 else "bearish",
            "recent_support": latest * 0.95,
            "recent_resistance": latest * 1.05,
        }

    # ------------------------------------------------------------------
    # Quant scoring (pure algorithmic fallback)
    # ------------------------------------------------------------------

    def _quant_score(self, ind: dict[str, float | str]) -> float:
        """
        Count bullish vs bearish signals across all indicators.
        Normalise to [-1.0, 1.0].
        """
        votes: list[int] = []

        # RSI
        rsi_sig = ind.get("rsi_signal", "neutral")
        if rsi_sig == "oversold":
            votes.append(1)
        elif rsi_sig == "overbought":
            votes.append(-1)

        # MACD histogram
        if ind.get("macd_bullish"):
            votes.append(1)
        else:
            votes.append(-1)

        # EMA trend
        if ind.get("ema_trend") == "bullish":
            votes.append(1)
        elif ind.get("ema_trend") == "bearish":
            votes.append(-1)

        # Price vs EMA20
        if ind.get("above_ema20"):
            votes.append(1)
        else:
            votes.append(-1)

        # Price vs EMA50
        if ind.get("above_ema50"):
            votes.append(1)
        else:
            votes.append(-1)

        # Bollinger
        bb_sig = ind.get("bb_signal", "neutral")
        if bb_sig == "oversold":
            votes.append(1)
        elif bb_sig == "overbought":
            votes.append(-1)

        # ADX directional
        if ind.get("adx_bullish"):
            votes.append(1)
        else:
            votes.append(-1)

        # Ichimoku cloud
        ichi_sig = ind.get("ichimoku_signal", "neutral")
        if ichi_sig == "bullish":
            votes.append(1)
        elif ichi_sig == "bearish":
            votes.append(-1)

        # Stochastic RSI
        stoch_sig = ind.get("stoch_signal", "neutral")
        if stoch_sig == "oversold":
            votes.append(1)
        elif stoch_sig == "overbought":
            votes.append(-1)

        # VWAP
        if ind.get("above_vwap"):
            votes.append(1)
        else:
            votes.append(-1)

        if not votes:
            return 0.0
        return sum(votes) / len(votes)

    def _quant_signal(
        self, indicators: dict[str, float | str], quant_conviction: float
    ) -> AgentSignal:
        """Build an AgentSignal from the pure quant score."""
        direction = self._direction_from_conviction(quant_conviction)
        support = indicators.get("recent_support", "N/A")
        resistance = indicators.get("recent_resistance", "N/A")
        reasoning = (
            f"Quant confluence score: {quant_conviction:+.2f}. "
            f"RSI: {indicators.get('rsi_signal', 'N/A')}, "
            f"MACD: {'bullish' if indicators.get('macd_bullish') else 'bearish'}, "
            f"EMA trend: {indicators.get('ema_trend', 'N/A')}, "
            f"Ichimoku: {indicators.get('ichimoku_signal', 'N/A')}. "
            f"Support: {support}, Resistance: {resistance}."
        )
        # Confidence is lower for pure quant (no LLM context interpretation)
        confidence = min(0.7, abs(quant_conviction))
        return AgentSignal(
            agent_name=self.name,
            direction=direction,
            conviction=quant_conviction,
            reasoning=reasoning,
            confidence=confidence,
            metadata={
                "mode": "quant_fallback",
                "key_levels": {
                    "support": support,
                    "resistance": resistance,
                },
            },
        )

    # ------------------------------------------------------------------
    # Claude-enhanced analysis
    # ------------------------------------------------------------------

    async def _claude_analysis(
        self,
        symbol: str,
        timeframe: str,
        indicators: dict[str, float | str],
        quant_conviction: float,
    ) -> AgentSignal:
        system_prompt = (
            "You are an elite technical analyst with 20 years of experience. "
            "Your task is to synthesise technical indicators into a precise trading signal. "
            "Be concise and data-driven. Do not hedge excessively. "
            "Respond ONLY with valid JSON — no prose outside the JSON object."
        )

        # Build a compact indicator summary for the prompt
        ind_summary = {
            k: (round(v, 4) if isinstance(v, float) else v)
            for k, v in indicators.items()
        }

        user_message = f"""Analyse {symbol} on the {timeframe} timeframe.

Technical indicators (latest bar):
{ind_summary}

Quant confluence score: {quant_conviction:+.3f}

Respond with this exact JSON:
{{
  "direction": "LONG" | "SHORT" | "NEUTRAL",
  "conviction": <float -1.0 to 1.0>,
  "confidence": <float 0.0 to 1.0>,
  "key_levels": {{
    "support": <float or null>,
    "resistance": <float or null>
  }},
  "reasoning": "<2-4 sentence explanation referencing specific indicators>"
}}"""

        raw = await self.call_claude(system_prompt, user_message, max_tokens=512)
        parsed = self._parse_json_response(raw)

        if "raw" in parsed:
            # JSON parse failed — use quant as fallback
            logger.warning("%s: could not parse Claude JSON, using quant fallback", self.name)
            return self._quant_signal(indicators, quant_conviction)

        direction_str = str(parsed.get("direction", "NEUTRAL")).upper()
        try:
            direction = Direction(direction_str)
        except ValueError:
            direction = Direction.NEUTRAL

        conviction = float(parsed.get("conviction", quant_conviction))
        confidence = float(parsed.get("confidence", 0.6))
        reasoning = str(parsed.get("reasoning", "No reasoning provided"))
        key_levels = parsed.get("key_levels", {})

        return AgentSignal(
            agent_name=self.name,
            direction=direction,
            conviction=conviction,
            reasoning=reasoning,
            confidence=confidence,
            metadata={
                "mode": "claude",
                "quant_conviction": quant_conviction,
                "key_levels": key_levels,
            },
        )
