"""
tests/test_crypto_acb.py
------------------------
Known-answer tests for cfo/crypto_acb.py — the standalone weighted-average
ACB engine that produces T5008 export rows for CRA filing.

This module is parallel to (not redundant with) finance/tax.py — that one
serves the live-trade datastream; this one ingests CSV-only history. Both
must agree on ACB math, which is what these tests anchor.

Run:
    python -m pytest tests/test_crypto_acb.py -v
"""

from __future__ import annotations

from datetime import date

import pytest

from cfo.crypto_acb import (
    AcbEngine,
    TradeRow,
    _apply_inclusion,
)


def _row(d: str, sym: str, side: str, qty: float, price: float, fee: float = 0) -> TradeRow:
    return TradeRow(
        date_val=date.fromisoformat(d),
        exchange="Kraken",
        symbol=sym,
        side=side,
        quantity=qty,
        price_cad=price,
        fee_cad=fee,
        notes="",
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Inclusion rate
# ─────────────────────────────────────────────────────────────────────────────

class TestInclusionRate:
    def test_loss_zero_taxable(self) -> None:
        amt, rate = _apply_inclusion(-1_000)
        assert amt == 0
        assert rate == 0.5

    def test_small_gain_half_inclusion(self) -> None:
        amt, rate = _apply_inclusion(20_000)
        assert amt == pytest.approx(10_000)
        assert rate == 0.5

    def test_above_threshold_blended(self) -> None:
        amt, rate = _apply_inclusion(300_000)
        expected = 250_000 * 0.5 + 50_000 * (2 / 3)
        assert amt == pytest.approx(expected, abs=0.01)


# ─────────────────────────────────────────────────────────────────────────────
#  Single-symbol ACB
# ─────────────────────────────────────────────────────────────────────────────

class TestSingleSymbolAcb:
    def test_single_buy_then_full_sell(self) -> None:
        trades = [
            _row("2024-01-15", "BTC", "buy", 0.5, 45_000),
            _row("2024-06-15", "BTC", "sell", 0.5, 60_000),
        ]
        result = AcbEngine().process(trades, 2024)
        s = result["summary"]
        assert s["disposition_count"] == 1
        # Proceeds = 0.5 * 60_000 = 30_000
        # Cost basis = 0.5 * 45_000 = 22_500
        # Gain = 7_500
        assert s["total_proceeds_cad"] == pytest.approx(30_000)
        assert s["total_cost_basis_cad"] == pytest.approx(22_500)
        assert s["capital_gains_cad"] == pytest.approx(7_500)
        assert s["taxable_amount_cad"] == pytest.approx(3_750)

    def test_partial_disposition_carries_remaining_acb(self) -> None:
        """
        Buy 1 BTC @ $40K. Sell 0.4 BTC @ $50K.
        Remaining: 0.6 BTC at the same $40K ACB/unit.
        """
        trades = [
            _row("2024-01-15", "BTC", "buy", 1.0, 40_000),
            _row("2024-06-15", "BTC", "sell", 0.4, 50_000),
        ]
        result = AcbEngine().process(trades, 2024)
        # Sold portion: 0.4 * 50_000 = 20_000 proceeds
        # Cost basis: 0.4 * 40_000 = 16_000
        # Gain: 4_000
        assert result["summary"]["capital_gains_cad"] == pytest.approx(4_000)
        # Carry-forward: 0.6 BTC remaining at $40K/unit
        assert result["units_held"]["BTC"] == pytest.approx(0.6)
        assert result["acb_per_symbol"]["BTC"] == pytest.approx(40_000, rel=0.001)

    def test_weighted_average_two_buys_then_sell(self) -> None:
        """
        Buy 1 BTC @ $40K, buy 1 BTC @ $60K  → ACB = $50K/coin.
        Sell 1 BTC @ $70K → gain = $20K (70K - 50K).
        """
        trades = [
            _row("2024-01-15", "BTC", "buy", 1.0, 40_000),
            _row("2024-02-15", "BTC", "buy", 1.0, 60_000),
            _row("2024-06-15", "BTC", "sell", 1.0, 70_000),
        ]
        result = AcbEngine().process(trades, 2024)
        assert result["summary"]["capital_gains_cad"] == pytest.approx(20_000)
        assert result["acb_per_symbol"]["BTC"] == pytest.approx(50_000)

    def test_fees_increase_acb_and_reduce_proceeds(self) -> None:
        """
        Buy 1 BTC @ $40K + $100 fee → cost basis = $40,100.
        Sell 1 BTC @ $50K - $100 fee → proceeds = $49,900.
        Gain = $9,800.
        """
        trades = [
            _row("2024-01-15", "BTC", "buy", 1.0, 40_000, fee=100),
            _row("2024-06-15", "BTC", "sell", 1.0, 50_000, fee=100),
        ]
        result = AcbEngine().process(trades, 2024)
        assert result["summary"]["capital_gains_cad"] == pytest.approx(9_800)


# ─────────────────────────────────────────────────────────────────────────────
#  Multi-symbol independence (BTC trades must not pollute ETH ACB)
# ─────────────────────────────────────────────────────────────────────────────

class TestMultiSymbolAcb:
    def test_btc_and_eth_are_independent(self) -> None:
        trades = [
            _row("2024-01-15", "BTC", "buy", 1.0, 40_000),
            _row("2024-01-20", "ETH", "buy", 5.0, 4_000),
            _row("2024-06-15", "BTC", "sell", 1.0, 50_000),  # +10K gain
            _row("2024-09-15", "ETH", "sell", 5.0, 3_000),   # -5K loss
        ]
        result = AcbEngine().process(trades, 2024)
        assert result["summary"]["capital_gains_cad"] == pytest.approx(10_000)
        assert result["summary"]["capital_losses_cad"] == pytest.approx(5_000)
        assert result["summary"]["net_gain_cad"] == pytest.approx(5_000)
        assert result["units_held"]["BTC"] == 0
        assert result["units_held"]["ETH"] == 0


# ─────────────────────────────────────────────────────────────────────────────
#  Cross-year ACB carry-forward
# ─────────────────────────────────────────────────────────────────────────────

class TestCrossYearAcb:
    def test_buy_2023_sell_2024_only_appears_in_2024(self) -> None:
        trades = [
            _row("2023-06-15", "BTC", "buy", 1.0, 30_000),
            _row("2024-03-15", "BTC", "sell", 1.0, 50_000),
        ]
        engine = AcbEngine()
        s2024 = engine.process(trades, 2024)
        engine2 = AcbEngine()
        s2023 = engine2.process(trades, 2023)
        assert s2024["summary"]["capital_gains_cad"] == pytest.approx(20_000)
        assert s2023["summary"]["capital_gains_cad"] == 0
        assert s2023["summary"]["disposition_count"] == 0


# ─────────────────────────────────────────────────────────────────────────────
#  Superficial loss flag (CRA GAAR risk)
# ─────────────────────────────────────────────────────────────────────────────

class TestSuperficialLoss:
    def test_loss_then_rebuy_within_30d_is_flagged(self) -> None:
        """
        Buy 1 BTC at $50K, sell at $40K (loss = $10K),
        re-buy 1 BTC 10 days later → CRA superficial-loss flag.
        """
        trades = [
            _row("2024-01-01", "BTC", "buy", 1.0, 50_000),
            _row("2024-06-01", "BTC", "sell", 1.0, 40_000),
            _row("2024-06-10", "BTC", "buy", 1.0, 38_000),
        ]
        result = AcbEngine().process(trades, 2024)
        assert any("SUPERFICIAL LOSS" in f for f in result["superficial_loss_flags"])

    def test_loss_then_rebuy_after_30d_no_flag(self) -> None:
        trades = [
            _row("2024-01-01", "BTC", "buy", 1.0, 50_000),
            _row("2024-06-01", "BTC", "sell", 1.0, 40_000),
            _row("2024-07-15", "BTC", "buy", 1.0, 38_000),
        ]
        result = AcbEngine().process(trades, 2024)
        assert result["superficial_loss_flags"] == []


# ─────────────────────────────────────────────────────────────────────────────
#  T5008 export rows
# ─────────────────────────────────────────────────────────────────────────────

class TestT5008Output:
    def test_t5008_boxes_match_disposition_math(self) -> None:
        trades = [
            _row("2024-01-15", "BTC", "buy", 1.0, 40_000),
            _row("2024-06-15", "BTC", "sell", 1.0, 55_000),
        ]
        result = AcbEngine().process(trades, 2024)
        assert len(result["dispositions"]) == 1
        d = result["dispositions"][0]
        assert d["t5008_box_131"] == pytest.approx(55_000)  # proceeds
        assert d["t5008_box_132"] == pytest.approx(40_000)  # ACB
        assert d["t5008_box_135"] == pytest.approx(15_000)  # gain
        assert d["type"] == "GAIN"
