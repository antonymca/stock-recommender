import math
from stock_signal import Config, compute_buy_timing, pick_strategies


def test_buy_timing_uptrend_macd_rsi_band():
    ind = {
        "price": 110.0,
        "sma20": 105.0,
        "sma50": 102.0,
        "sma200": 100.0,
        "macd": 1.0,
        "macd_signal": 0.5,
        "rsi14": 55.0,
    }
    cfg = Config()
    res = compute_buy_timing(ind, cfg)
    assert res["buy_signal"] is True
    assert "Price > SMA200" in ";".join(res["rationale"])
    assert res["timing_note"].startswith("Scale-in 50% now")


def test_strategy_selection_iv_regimes():
    cfg = Config()
    low_iv = pick_strategies(px=100, iv_rank=10, holding_shares=0, cfg=cfg)
    assert low_iv[0]["name"] == "Bull Call Debit Spread"

    high_iv = pick_strategies(px=100, iv_rank=40, holding_shares=0, cfg=cfg)
    names = [s["name"] for s in high_iv]
    assert "Bull Put Credit Spread" in names and "Cash-Secured Put" in names

    cc = pick_strategies(px=100, iv_rank=10, holding_shares=150, cfg=cfg)
    names = [s["name"] for s in cc]
    assert "Covered Call" in names


def test_spread_risk_math():
    cfg = Config()
    bc = pick_strategies(px=100, iv_rank=10, holding_shares=0, cfg=cfg)[0]
    assert math.isclose(bc["estimates"]["net_debit"], cfg.bull_call_width * 0.25)
    assert math.isclose(
        bc["estimates"]["max_profit"], cfg.bull_call_width - cfg.bull_call_width * 0.25
    )

    bp = pick_strategies(px=100, iv_rank=40, holding_shares=0, cfg=cfg)[0]
    assert math.isclose(bp["estimates"]["net_credit"], cfg.bull_put_width * 0.25)
    assert math.isclose(
        bp["estimates"]["max_loss"], cfg.bull_put_width - cfg.bull_put_width * 0.25
    )
